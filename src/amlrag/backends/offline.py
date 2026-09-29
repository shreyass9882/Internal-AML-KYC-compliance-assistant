"""Offline stand-ins for Ollama, used by the test suite and for UI development.

HashEmbedder: deterministic feature-hashing embeddings (bag of words + bigrams).
StubLLM:      keyword heuristics that emit schema-valid JSON citing retrieved sources.

Neither produces real compliance answers. The server shows a red "offline stub"
banner whenever the stub generator is active.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from amlrag.textutil import content_words, tokenize


class HashEmbedder:
    def __init__(self, dim: int = 512):
        self.dim = dim
        self.name = f"hash:{dim}"

    def _vec(self, text: str) -> list[float]:
        toks = tokenize(text)
        feats = toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:])]
        v = [0.0] * self.dim
        for f in feats:
            h = int.from_bytes(hashlib.blake2b(f.encode(), digest_size=8).digest(), "little")
            v[h % self.dim] += 1.0 if (h >> 63) & 1 else -1.0
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)


_SOURCE_RE = re.compile(r"^\[(S\d+)\]\s*(.*)$", re.M)


def _sources_from_prompt(text: str) -> list[tuple[str, str]]:
    """Return (label, block text) pairs from a prompt built by generate.prompts."""
    matches = list(_SOURCE_RE.finditer(text))
    out = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group(1), text[m.start():end]))
    return out


def _body(block: str) -> str:
    return block.split("\n", 1)[1].strip() if "\n" in block else ""


def _best_sources(query: str, sources: list[tuple[str, str]], n: int = 2) -> list[str]:
    q = content_words(query)
    scored = sorted(sources, key=lambda s: -len(q & content_words(s[1])))
    return [label for label, _ in scored[:n]]


def _stub_facts(scenario: str) -> dict[str, Any]:
    s = scenario.lower()
    pep = "unknown"
    if "foreign" in s and ("pep" in s or "politically exposed" in s or "minister" in s):
        pep = "foreign"
    elif "politically exposed" in s or " pep" in s or "parliament" in s:
        pep = "domestic"
    elif "not a pep" in s or "no pep" in s:
        pep = "none"
    ctype = "unknown"
    for key, label in (("trust", "trust"), ("sole trader", "sole_trader"), ("partnership", "partnership"),
                       ("government", "government_body"), ("company", "company"), ("pty", "company"),
                       ("association", "unincorporated_association"), ("individual", "individual")):
        if key in s:
            ctype = label
            break
    risk = "high" if "high risk" in s or "high-risk customer" in s else ("low" if "low risk" in s or "low-risk" in s else "unknown")
    return {
        "customer_type": ctype,
        "pep_status": pep,
        "pep_same_country_foreign_branch": False,
        "high_risk_jurisdiction": bool(re.search(r"call for action|high[- ]risk (jurisdiction|country)", s)),
        "suspicious_matter_continuing": "suspicious matter" in s,
        "nested_services": "nested" in s or "correspondent" in s,
        "unusual_transaction": bool(re.search(r"no (apparent|clear) (business|lawful|economic) purpose|unusually (large|complex)", s)),
        "virtual_assets_with_cash": "virtual asset" in s and "cash" in s,
        "regulated_or_government": bool(re.search(r"government|apra|listed on|asx", s)),
        "ml_tf_risk": risk,
        "delayed_verification": "delay" in s,
        "missing_information": [] if len(s) > 60 else ["customer type", "risk rating"],
    }


class StubLLM:
    name = "stub"

    def chat_json(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None,
                  task: str = "") -> tuple[dict[str, Any], dict[str, Any]]:
        user = messages[-1]["content"]
        stats = {"latency_s": 0.0, "model": "stub", "task": task}
        if task == "facts":
            scenario = user.split("SCENARIO:", 1)[-1]
            return _stub_facts(scenario), stats

        sources = _sources_from_prompt(user)
        query = user.split("SCENARIO:", 1)[-1].split("QUESTION:", 1)[-1].split("SOURCES:", 1)[0]

        if task == "judge":
            claim = user.split("CLAIM:", 1)[-1].split("PASSAGES:", 1)[0]
            passages = user.split("PASSAGES:", 1)[-1]
            cw = content_words(claim)
            overlap = len(cw & content_words(passages)) / max(1, len(cw))
            return {"supported": overlap >= 0.5, "reason": f"lexical overlap {overlap:.2f}"}, stats

        if not sources:
            payload = {"summary": "The provided sources do not cover this question.", "confidence": "low",
                       "missing_information": ["relevant guidance"]}
            if task == "determine":
                payload.update({"tier": "insufficient_information", "reasoning": [], "required_measures": []})
            else:
                payload.update({"answerable": False, "key_points": []})
            return payload, stats

        cited = _best_sources(query, sources)
        if task == "explain":
            return {
                "answerable": True,
                "summary": "Offline stub answer. See the cited sources for the actual obligation.",
                "key_points": [{"point": _body(dict(sources)[cited[0]])[:220], "sources": cited[:1]}],
                "confidence": "medium",
                "missing_information": [],
            }, stats

        f = _stub_facts(query)
        if (f["pep_status"] == "foreign" or f["high_risk_jurisdiction"] or f["suspicious_matter_continuing"]
                or f["nested_services"] or f["unusual_transaction"] or f["ml_tf_risk"] == "high"):
            tier = "enhanced"
        elif f["regulated_or_government"] and f["ml_tf_risk"] != "high":
            tier = "simplified"
        elif f["missing_information"]:
            tier = "insufficient_information"
        else:
            tier = "standard"
        point_text = _body(dict(sources)[cited[0]])[:220]
        return {
            "tier": tier,
            "summary": f"Offline stub determination: {tier.replace('_', ' ')}.",
            "reasoning": [{"point": point_text, "sources": cited[:1]}],
            "required_measures": [{"measure": "Collect and verify KYC information.", "sources": cited[-1:]}],
            "missing_information": f["missing_information"],
            "confidence": "medium" if tier != "insufficient_information" else "low",
        }, stats
