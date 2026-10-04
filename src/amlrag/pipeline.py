"""End-to-end assistant: retrieve -> (facts) -> generate -> verify -> guardrails."""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from amlrag import ABSTAIN
from amlrag.backends import index_dir, make_embedder, make_llm
from amlrag.config import Config
from amlrag.generate.guardrails import apply_guardrails
from amlrag.generate.prompts import (
    CLOSED_DETERMINE_SCHEMA,
    CLOSED_EXPLAIN_SCHEMA,
    DETERMINE_SCHEMA,
    EXPLAIN_SCHEMA,
    PROMPT_VERSION,
    RETRY_UNCITED,
    closed_determine_messages,
    closed_explain_messages,
    determine_messages,
    explain_messages,
)
from amlrag.generate.references import check_reference, parse_references
from amlrag.generate.verify import cap_confidence, verify
from amlrag.index.store import VectorStore
from amlrag.ingest.build import read_chunks
from amlrag.ingest.fetch import snapshot_date
from amlrag.models import Retrieved
from amlrag.retrieve.facts import extract_facts, mentions_fact, sub_queries
from amlrag.retrieve.hybrid import Retriever

log = logging.getLogger(__name__)

DETERMINE_GROUPS = {"reasoning": "point", "required_measures": "measure"}

# System-generated reasons for flagging an answer. Stored in the query log instead of
# the model's own wording, which can repeat customer names from the question.
FLAG_NO_GUIDANCE = "No guidance in the knowledge base was close enough to answer"
FLAG_MODEL_ERROR = "The language model failed to respond"
FLAG_NO_CITATION = "Answer withheld: no valid citation"
FLAG_MODEL_ABSTAINED = "The model could not answer from the sources"
FLAG_ESCALATED = "Tier escalated by guardrail"
FLAG_CLOSED_BOOK = "Closed-book baseline: no sources retrieved"
FLAG_UNDESCRIBED = "The scenario does not describe the customer"

# A scenario this short with no extracted facts at all ("A customer wants to open an account")
# can't support any tier. The model is told so, but an 8-9B model still tends to answer "standard".
_UNDESCRIBED_MAX_WORDS = 30


# Wording that presents something as not known. Used to catch an answer that calls a fact the
# scenario explicitly denies "not stated" (adversarial test A01).
_UNKNOWN_WORDS = ("not state", "not say", "doesn't say", "not specif", "not mention", "unknown", "unclear",
                  "not known", "not clear", "no information", "not provided", "not given")


def ruled_out_called_unknown(facts: dict[str, Any] | None, texts: list[str], missing: list[str]) -> list[str]:
    """Sentences that treat a fact the scenario rules out as unknown.

    Flags (never removes) a missing_information item about a ruled-out fact, and a reasoning or
    summary sentence that both mentions a ruled-out fact and calls it unstated. A wrongly ruled-out
    fact must not silently hide a real gap, so these become a warning for the reviewer.
    """
    ruled = list((facts or {}).get("ruled_out") or [])
    if not ruled:
        return []
    hits = [m for m in missing if any(mentions_fact(m, k) for k in ruled)]
    for t in texts:
        low = t.lower()
        if any(w in low for w in _UNKNOWN_WORDS) and any(mentions_fact(t, k) for k in ruled):
            hits.append(t)
    return hits


def undescribed_customer(facts: dict[str, Any] | None, scenario: str) -> bool:
    """True when a short scenario gives nothing to decide a tier on: no customer type, risk, PEP or trigger."""
    if not facts or len(scenario.split()) > _UNDESCRIBED_MAX_WORDS:
        return False
    any_trigger = any(v is True for v in facts.values())
    return (facts.get("customer_type") in (None, "unknown") and facts.get("ml_tf_risk") in (None, "unknown")
            and facts.get("pep_status") in (None, "unknown", "none") and not any_trigger)
CLOSED_BOOK_WARNING = ("Closed-book baseline: this answer comes from the model's own training with no retrieved "
                       "sources. Its references were checked only for whether the section exists in the snapshot.")
EXPLAIN_GROUPS = {"key_points": "point"}


class Assistant:
    def __init__(self, cfg: Config, retriever: Retriever, llm, embedder_name: str, snapshot: str | None = None):
        self.cfg = cfg
        self.retriever = retriever
        self.llm = llm
        self.embedder_name = embedder_name
        self.snapshot = snapshot

    @classmethod
    def from_config(cls, cfg: Config, llm=None) -> "Assistant":
        embedder = make_embedder(cfg)
        chunks = read_chunks(cfg.path("chunks_file"))
        store = VectorStore(index_dir(cfg), cfg.retrieval.collection, embedder, chunks)
        retriever = Retriever.from_config(chunks, store, cfg.retrieval)
        return cls(cfg, retriever, llm or make_llm(cfg), embedder.name,
                   store.manifest.get("snapshot") or snapshot_date(cfg))

    @property
    def offline_stub(self) -> bool:
        return getattr(self.llm, "name", "") == "stub"

    @property
    def closed_book(self) -> bool:
        return not self.cfg.retrieval.get("enabled", True)

    # ------------------------------------------------------------------ helpers
    def _sources(self, results: list[Retrieved], cited: list[str]) -> list[dict[str, Any]]:
        out = []
        for i, r in enumerate(results, start=1):
            label = f"S{i}"
            out.append({**r.to_dict(), "label": label, "text": r.chunk.text, "heading_path": r.chunk.heading_path,
                        "cited": label in cited, "last_updated": r.chunk.last_updated})
        return out

    def _abstain(self, mode: str, query: str, reason: str, results: list[Retrieved], facts, timings,
                 flag_reason: str, missing: list[str] | None = None) -> dict[str, Any]:
        return {
            "mode": mode, "query": query, "tier": ABSTAIN if mode == "determine" else None, "model_tier": None,
            "summary": reason, "points": [], "missing_information": missing or [], "confidence": "low",
            "abstained": True, "abstain_reason": reason, "flag_reason": flag_reason, "needs_review": True,
            "warnings": [],
            "facts": facts, "sources": self._sources(results, []), "checks": {}, "timings": timings,
            "models": {"embedder": self.embedder_name, "generator": getattr(self.llm, "name", "?")},
            "snapshot": self.snapshot, "offline_stub": self.offline_stub, "prompt_version": PROMPT_VERSION,
        }

    def _retrieve(self, text: str, facts) -> tuple[list[Retrieved], float]:
        t0 = time.perf_counter()
        results = self.retriever.search(text, sub_queries(facts))
        return results, time.perf_counter() - t0

    def _retry_uncited(self, messages, out, schema, task, label_map, groups, scenario=None):
        """Ask once more when the model answered but cited nothing, so the answer would be withheld.

        This repairs the format only: the retry sees the same sources and instructions plus its
        own first answer. Returns (output, verification) if the retry cites something, else None.
        """
        retry = messages + [{"role": "assistant", "content": json.dumps(out, ensure_ascii=False)},
                            {"role": "user", "content": RETRY_UNCITED}]
        try:
            out2, _ = self.llm.chat_json(retry, schema, task=task)
        except Exception:
            log.warning("retry after an uncited answer failed", exc_info=True)
            return None
        ver2 = verify(out2, label_map, self.cfg.verification.min_support_overlap, groups, scenario)
        return (out2, ver2) if ver2.cited_labels else None

    # -------------------------------------------------------------------- modes
    def determine(self, scenario: str) -> dict[str, Any]:
        if self.closed_book:
            return self._closed_book("determine", scenario)
        t_start = time.perf_counter()
        timings: dict[str, float] = {}
        facts = None
        if self.cfg.retrieval.use_fact_extraction:
            t0 = time.perf_counter()
            facts, _ = extract_facts(self.llm, scenario)
            timings["facts_s"] = round(time.perf_counter() - t0, 3)
        results, t_ret = self._retrieve(scenario, facts)
        timings["retrieval_s"] = round(t_ret, 3)

        max_sim = Retriever.max_similarity(results)
        if not results or max_sim < self.cfg.retrieval.min_dense_similarity:
            timings["total_s"] = round(time.perf_counter() - t_start, 3)
            return self._abstain("determine", scenario,
                                 "The knowledge base has no guidance close enough to this scenario to make a "
                                 "determination. Check the scenario is about customer due diligence, or escalate.",
                                 results, facts, timings, FLAG_NO_GUIDANCE)

        messages, label_map = determine_messages(scenario, results, facts)
        t0 = time.perf_counter()
        try:
            out, stats = self.llm.chat_json(messages, DETERMINE_SCHEMA, task="determine")
        except Exception as exc:
            log.exception("generation failed")
            timings["total_s"] = round(time.perf_counter() - t_start, 3)
            return self._abstain("determine", scenario, f"The language model failed to answer ({exc}).",
                                 results, facts, timings, FLAG_MODEL_ERROR)
        retried = False
        if out.get("tier") != ABSTAIN and not verify(out, label_map, self.cfg.verification.min_support_overlap,
                                                      DETERMINE_GROUPS, scenario).cited_labels:
            fixed = self._retry_uncited(messages, out, DETERMINE_SCHEMA, "determine", label_map,
                                        DETERMINE_GROUPS, scenario)
            if fixed:
                out, retried = fixed[0], True
        timings["generation_s"] = round(time.perf_counter() - t0, 3)

        model_tier = out.get("tier") if out.get("tier") in DETERMINE_SCHEMA["properties"]["tier"]["enum"] else ABSTAIN
        warnings: list[str] = []
        guard = {"tier": model_tier, "warnings": [], "escalated": False, "added_points": [], "fired": []}
        if self.cfg.verification.guardrails and model_tier != ABSTAIN:
            guard = apply_guardrails(model_tier, facts, label_map, self.cfg.verification.guardrail_mode)
            warnings += guard["warnings"]
            out.setdefault("reasoning", [])
            out["reasoning"] = list(out["reasoning"]) + guard["added_points"]

        ver = verify(out, label_map, self.cfg.verification.min_support_overlap, DETERMINE_GROUPS, scenario)
        confidence, notes = cap_confidence(str(out.get("confidence", "low")), ver,
                                           self.cfg.verification.max_unsupported_share)
        warnings += notes
        final_tier = guard["tier"]
        undescribed = final_tier == "standard" and undescribed_customer(facts, scenario)
        if undescribed:
            final_tier = ABSTAIN

        abstained = final_tier == ABSTAIN
        abstain_reason = flag_reason = None
        if undescribed:
            abstain_reason = ("The scenario doesn't say who or what the customer is, so no CDD tier can be determined. "
                              "Describe the customer: their type (individual, company, trust...), risk rating, and "
                              "any PEP or high-risk country links.")
            flag_reason = FLAG_UNDESCRIBED
        elif not abstained and not ver.cited_labels:
            abstained, final_tier = True, ABSTAIN
            abstain_reason = "The model gave a determination without any valid citation, so it was withheld."
            flag_reason = FLAG_NO_CITATION
        elif abstained:
            abstain_reason = out.get("summary") or "The sources do not support a determination."
            flag_reason = FLAG_MODEL_ABSTAINED
        elif guard["escalated"]:
            flag_reason = FLAG_ESCALATED

        missing = [str(m) for m in out.get("missing_information", [])]
        called_unknown = ruled_out_called_unknown(
            facts, [p.text for p in ver.points.get("reasoning", [])] + [str(out.get("summary", ""))], missing)
        if called_unknown and not undescribed:
            warnings.append("The answer treats something the scenario rules out as unknown. Check it against the "
                            "scenario: " + "; ".join(f'"{t[:90]}"' for t in called_unknown[:2]))
        measures = ver.points.get("required_measures", [])

        points = [{"group": g, **p.to_dict(label_map)} for g, ps in ver.points.items() for p in ps]
        timings["total_s"] = round(time.perf_counter() - t_start, 3)
        return {
            "mode": "determine", "query": scenario, "tier": final_tier, "model_tier": model_tier,
            # When no customer is described, the model's own (tier-giving) reasoning is withheld.
            "summary": abstain_reason if undescribed else str(out.get("summary", "")).strip(),
            "points": [] if undescribed else points,
            "missing_information": missing,
            "confidence": "low" if abstained else confidence, "abstained": abstained,
            "abstain_reason": abstain_reason, "flag_reason": flag_reason,
            "needs_review": abstained or confidence == "low" or bool(warnings),
            "warnings": warnings, "facts": facts, "guardrails_fired": guard["fired"],
            "escalated": guard["escalated"], "sources": self._sources(results, ver.cited_labels),
            "checks": {"citation_validity": round(ver.citation_validity, 3), "points": len(ver.all_points),
                       "unsupported_points": len(ver.unsupported), "uncited_points": len(ver.uncited),
                       "max_similarity": round(max_sim, 4), "retried_uncited": retried,
                       # Citation validity says each citation points to a retrieved passage; supported_points
                       # says how many points their cited text actually backs (lexical check). Not the same.
                       "supported_points": len(ver.all_points) - len(ver.unsupported),
                       "ruled_out_called_unknown": len(called_unknown) if not undescribed else 0,
                       "required_measures": sum(1 for p in measures if p.required is True),
                       "optional_measures": sum(1 for p in measures if p.required is False)},
            "timings": timings, "llm_stats": stats,
            "models": {"embedder": self.embedder_name, "generator": getattr(self.llm, "name", "?")},
            "snapshot": self.snapshot, "offline_stub": self.offline_stub, "prompt_version": PROMPT_VERSION,
        }

    def explain(self, question: str) -> dict[str, Any]:
        if self.closed_book:
            return self._closed_book("explain", question)
        t_start = time.perf_counter()
        timings: dict[str, float] = {}
        results, t_ret = self._retrieve(question, None)
        timings["retrieval_s"] = round(t_ret, 3)
        max_sim = Retriever.max_similarity(results)
        if not results or max_sim < self.cfg.retrieval.min_dense_similarity:
            timings["total_s"] = round(time.perf_counter() - t_start, 3)
            return self._abstain("explain", question,
                                 "The knowledge base does not cover this question. It currently holds AUSTRAC "
                                 "customer due diligence guidance and Part 6 of the AML/CTF Rules 2025.",
                                 results, None, timings, FLAG_NO_GUIDANCE)
        messages, label_map = explain_messages(question, results)
        t0 = time.perf_counter()
        try:
            out, stats = self.llm.chat_json(messages, EXPLAIN_SCHEMA, task="explain")
        except Exception as exc:
            log.exception("generation failed")
            timings["total_s"] = round(time.perf_counter() - t_start, 3)
            return self._abstain("explain", question, f"The language model failed to answer ({exc}).",
                                 results, None, timings, FLAG_MODEL_ERROR)
        ver = verify(out, label_map, self.cfg.verification.min_support_overlap, EXPLAIN_GROUPS)
        retried = False
        if out.get("answerable", True) and not ver.cited_labels:
            fixed = self._retry_uncited(messages, out, EXPLAIN_SCHEMA, "explain", label_map, EXPLAIN_GROUPS)
            if fixed:
                (out, ver), retried = fixed, True
        timings["generation_s"] = round(time.perf_counter() - t0, 3)
        confidence, notes = cap_confidence(str(out.get("confidence", "low")), ver,
                                           self.cfg.verification.max_unsupported_share)
        answerable = bool(out.get("answerable", True)) and bool(ver.cited_labels)
        points = [{"group": g, **p.to_dict(label_map)} for g, ps in ver.points.items() for p in ps]
        timings["total_s"] = round(time.perf_counter() - t_start, 3)
        return {
            "mode": "explain", "query": question, "tier": None, "model_tier": None,
            "summary": str(out.get("summary", "")).strip(), "points": points if answerable else [],
            "missing_information": [str(m) for m in out.get("missing_information", [])],
            "confidence": confidence if answerable else "low", "abstained": not answerable,
            "abstain_reason": None if answerable else (out.get("summary") or "The sources do not answer this."),
            "flag_reason": None if answerable else (FLAG_MODEL_ABSTAINED if not out.get("answerable", True)
                                                    else FLAG_NO_CITATION),
            "needs_review": (not answerable) or confidence == "low" or bool(notes), "warnings": notes,
            "facts": None, "sources": self._sources(results, ver.cited_labels if answerable else []),
            "checks": {"citation_validity": round(ver.citation_validity, 3), "points": len(ver.all_points),
                       "unsupported_points": len(ver.unsupported), "uncited_points": len(ver.uncited),
                       "max_similarity": round(max_sim, 4), "retried_uncited": retried,
                       "supported_points": len(ver.all_points) - len(ver.unsupported)},
            "timings": timings, "llm_stats": stats,
            "models": {"embedder": self.embedder_name, "generator": getattr(self.llm, "name", "?")},
            "snapshot": self.snapshot, "offline_stub": self.offline_stub, "prompt_version": PROMPT_VERSION,
        }

    # ------------------------------------------------------------ closed-book baseline
    def _snapshot_sections(self) -> tuple[set[str], set[str]]:
        if not hasattr(self, "_sections_cache"):
            chunks = self.retriever.chunks.values()
            self._sections_cache = ({c.section_ref for c in chunks}, {c.doc_id for c in chunks})
        return self._sections_cache

    def _closed_book(self, mode: str, text: str) -> dict[str, Any]:
        """Answer with no retrieval: the model's own knowledge, references parsed and existence-checked."""
        t_start = time.perf_counter()
        if mode == "determine":
            messages, schema, groups = closed_determine_messages(text), CLOSED_DETERMINE_SCHEMA, DETERMINE_GROUPS
        else:
            messages, schema, groups = closed_explain_messages(text), CLOSED_EXPLAIN_SCHEMA, EXPLAIN_GROUPS
        try:
            out, stats = self.llm.chat_json(messages, schema, task=f"closed_{mode}")
        except Exception as exc:
            log.exception("generation failed")
            res = self._abstain(mode, text, f"The language model failed to answer ({exc}).", [], None,
                                {"total_s": round(time.perf_counter() - t_start, 3)}, FLAG_MODEL_ERROR)
            return {**res, "closed_book": True}
        known, docs = self._snapshot_sections()
        points: list[dict[str, Any]] = []
        verifiable = valid = uncited = 0
        for key, field in groups.items():
            for item in out.get(key) or []:
                if not isinstance(item, dict) or not str(item.get(field, "")).strip():
                    continue
                ref_text = str(item.get("reference", "")).strip()
                refs = parse_references(ref_text)
                citations, invalid = [], []
                for ref in refs:
                    exists = check_reference(ref, known, docs)
                    if exists is not None:
                        verifiable += 1
                        valid += int(exists)
                    if exists is False:
                        invalid.append(ref)
                    citations.append({"label": ref, "chunk_id": ref, "citation": ref_text, "url": None,
                                      "exists": exists})
                uncited += int(not refs)
                points.append({"group": key, "text": str(item[field]).strip(), "reference": ref_text,
                               "citations": citations, "invalid_labels": invalid, "support": None,
                               "supported": None})
        if mode == "determine":
            tier = out.get("tier") if out.get("tier") in DETERMINE_SCHEMA["properties"]["tier"]["enum"] else ABSTAIN
            abstained = tier == ABSTAIN
        else:
            tier = None
            abstained = not bool(out.get("answerable", True)) or not points
        confidence = out.get("confidence") if out.get("confidence") in ("high", "medium", "low") else "low"
        return {
            "mode": mode, "query": text, "tier": tier, "model_tier": tier,
            "summary": str(out.get("summary", "")).strip(),
            "points": [] if (abstained and mode == "explain") else points,
            "missing_information": [str(m) for m in out.get("missing_information", [])],
            "confidence": "low" if abstained else confidence, "abstained": abstained,
            "abstain_reason": (out.get("summary") or "The model could not answer.") if abstained else None,
            "flag_reason": FLAG_CLOSED_BOOK, "needs_review": True, "warnings": [CLOSED_BOOK_WARNING],
            "facts": None, "guardrails_fired": [], "escalated": False, "sources": [], "closed_book": True,
            "checks": {"citation_validity": round(valid / verifiable, 3) if verifiable else None,
                       "references": sum(len(p["citations"]) for p in points), "verifiable_references": verifiable,
                       "points": len(points), "uncited_points": uncited, "unsupported_points": None},
            "timings": {"generation_s": stats.get("latency_s"), "total_s": round(time.perf_counter() - t_start, 3)},
            "llm_stats": stats,
            "models": {"embedder": None, "generator": getattr(self.llm, "name", "?")},
            "snapshot": self.snapshot, "offline_stub": self.offline_stub, "prompt_version": PROMPT_VERSION,
        }

    def ask(self, mode: str, text: str) -> dict[str, Any]:
        if mode == "determine":
            return self.determine(text)
        if mode == "explain":
            return self.explain(text)
        raise ValueError(f"unknown mode {mode!r}")
