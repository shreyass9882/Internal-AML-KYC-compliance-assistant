"""End-to-end assistant: retrieve -> (facts) -> generate -> verify -> guardrails."""
from __future__ import annotations

import logging
import time
from typing import Any

from amlrag import ABSTAIN
from amlrag.backends import make_embedder, make_llm
from amlrag.config import Config
from amlrag.generate.guardrails import apply_guardrails
from amlrag.generate.prompts import DETERMINE_SCHEMA, EXPLAIN_SCHEMA, determine_messages, explain_messages
from amlrag.generate.verify import cap_confidence, verify
from amlrag.index.store import VectorStore
from amlrag.ingest.build import read_chunks
from amlrag.ingest.fetch import snapshot_date
from amlrag.models import Retrieved
from amlrag.retrieve.facts import extract_facts, sub_queries
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
        store = VectorStore(cfg.path("chroma_dir"), cfg.retrieval.collection, embedder, chunks)
        retriever = Retriever.from_config(chunks, store, cfg.retrieval)
        return cls(cfg, retriever, llm or make_llm(cfg), embedder.name,
                   store.manifest.get("snapshot") or snapshot_date(cfg))

    @property
    def offline_stub(self) -> bool:
        return getattr(self.llm, "name", "") == "stub"

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
            "snapshot": self.snapshot, "offline_stub": self.offline_stub,
        }

    def _retrieve(self, text: str, facts) -> tuple[list[Retrieved], float]:
        t0 = time.perf_counter()
        results = self.retriever.search(text, sub_queries(facts))
        return results, time.perf_counter() - t0

    # -------------------------------------------------------------------- modes
    def determine(self, scenario: str) -> dict[str, Any]:
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
        timings["generation_s"] = round(time.perf_counter() - t0, 3)

        model_tier = out.get("tier") if out.get("tier") in DETERMINE_SCHEMA["properties"]["tier"]["enum"] else ABSTAIN
        warnings: list[str] = []
        guard = {"tier": model_tier, "warnings": [], "escalated": False, "added_points": [], "fired": []}
        if self.cfg.verification.guardrails and model_tier != ABSTAIN:
            guard = apply_guardrails(model_tier, facts, label_map, self.cfg.verification.guardrail_mode)
            warnings += guard["warnings"]
            out.setdefault("reasoning", [])
            out["reasoning"] = list(out["reasoning"]) + guard["added_points"]

        ver = verify(out, label_map, self.cfg.verification.min_support_overlap, DETERMINE_GROUPS)
        confidence, notes = cap_confidence(str(out.get("confidence", "low")), ver,
                                           self.cfg.verification.max_unsupported_share)
        warnings += notes
        final_tier = guard["tier"]

        abstained = final_tier == ABSTAIN
        abstain_reason = flag_reason = None
        if not abstained and not ver.cited_labels:
            abstained, final_tier = True, ABSTAIN
            abstain_reason = "The model gave a determination without any valid citation, so it was withheld."
            flag_reason = FLAG_NO_CITATION
        elif abstained:
            abstain_reason = out.get("summary") or "The sources do not support a determination."
            flag_reason = FLAG_MODEL_ABSTAINED
        elif guard["escalated"]:
            flag_reason = FLAG_ESCALATED

        points = [{"group": g, **p.to_dict(label_map)} for g, ps in ver.points.items() for p in ps]
        timings["total_s"] = round(time.perf_counter() - t_start, 3)
        return {
            "mode": "determine", "query": scenario, "tier": final_tier, "model_tier": model_tier,
            "summary": str(out.get("summary", "")).strip(), "points": points,
            "missing_information": [str(m) for m in out.get("missing_information", [])],
            "confidence": "low" if abstained else confidence, "abstained": abstained,
            "abstain_reason": abstain_reason, "flag_reason": flag_reason,
            "needs_review": abstained or confidence == "low" or bool(warnings),
            "warnings": warnings, "facts": facts, "guardrails_fired": guard["fired"],
            "escalated": guard["escalated"], "sources": self._sources(results, ver.cited_labels),
            "checks": {"citation_validity": round(ver.citation_validity, 3), "points": len(ver.all_points),
                       "unsupported_points": len(ver.unsupported), "uncited_points": len(ver.uncited),
                       "max_similarity": round(max_sim, 4)},
            "timings": timings, "llm_stats": stats,
            "models": {"embedder": self.embedder_name, "generator": getattr(self.llm, "name", "?")},
            "snapshot": self.snapshot, "offline_stub": self.offline_stub,
        }

    def explain(self, question: str) -> dict[str, Any]:
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
        timings["generation_s"] = round(time.perf_counter() - t0, 3)

        ver = verify(out, label_map, self.cfg.verification.min_support_overlap, EXPLAIN_GROUPS)
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
                       "max_similarity": round(max_sim, 4)},
            "timings": timings, "llm_stats": stats,
            "models": {"embedder": self.embedder_name, "generator": getattr(self.llm, "name", "?")},
            "snapshot": self.snapshot, "offline_stub": self.offline_stub,
        }

    def ask(self, mode: str, text: str) -> dict[str, Any]:
        if mode == "determine":
            return self.determine(text)
        if mode == "explain":
            return self.explain(text)
        raise ValueError(f"unknown mode {mode!r}")
