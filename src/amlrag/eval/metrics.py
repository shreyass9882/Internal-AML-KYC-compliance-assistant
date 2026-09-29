"""Evaluation metrics: effectiveness, retrieval, attribution, faithfulness, abstention, consistency."""
from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from typing import Any

from amlrag import ABSTAIN, TIER_ORDER, TIERS
from amlrag.eval.gold import GoldItem
from amlrag.models import ref_matches


def _mean(xs: list[float]) -> float | None:
    return round(sum(xs) / len(xs), 4) if xs else None


def _doc_of(ref: str) -> str:
    return ref.split("::", 1)[0]


def reachable_refs(item: GoldItem, available_docs: set[str]) -> list[str]:
    """Gold references whose document is actually in the index (e.g. the optional Act may be absent)."""
    return [r for r in item.expected_sections if _doc_of(r) in available_docs]


def key_fact_recall(answer_text: str, key_facts: list[list[str]]) -> float | None:
    if not key_facts:
        return None
    text = answer_text.lower()
    hits = sum(any(alt.lower() in text for alt in alts) for alts in key_facts)
    return hits / len(key_facts)


def _percentile(xs: list[float], q: float) -> float | None:
    if not xs:
        return None
    xs = sorted(xs)
    idx = min(len(xs) - 1, max(0, round(q * (len(xs) - 1))))
    return round(xs[idx], 2)


def compute_metrics(items: list[GoldItem], preds: dict[str, dict[str, Any]], available_docs: set[str],
                    k: int) -> dict[str, Any]:
    by_id = {i.id: i for i in items}
    pairs = [(by_id[pid], p) for pid, p in preds.items() if pid in by_id]
    m: dict[str, Any] = {"n_items": len(pairs), "k": k}

    # ------------------------------------------------------------ tier effectiveness
    det = [(g, p) for g, p in pairs if g.mode == "determine" and g.answerable]
    strict, accept, under, over, abst = [], [], [], [], []
    confusion: dict[str, Counter] = defaultdict(Counter)
    by_type: dict[str, list[float]] = defaultdict(list)
    for g, p in det:
        pred = p.get("tier") or ABSTAIN
        confusion[g.expected_tier][pred] += 1
        ok = pred in g.acceptable
        strict.append(float(pred == g.expected_tier))
        accept.append(float(ok))
        by_type[g.customer_type or "unspecified"].append(float(ok))
        if pred in TIER_ORDER:
            lo = min(TIER_ORDER[t] for t in g.acceptable if t in TIER_ORDER)
            hi = max(TIER_ORDER[t] for t in g.acceptable if t in TIER_ORDER)
            under.append(float(TIER_ORDER[pred] < lo))
            over.append(float(TIER_ORDER[pred] > hi))
            abst.append(0.0)
        else:
            under.append(0.0)
            over.append(0.0)
            abst.append(1.0)
    m["tier"] = {
        "n": len(det),
        "accuracy_strict": _mean(strict),
        "accuracy_acceptable": _mean(accept),
        "under_application_rate": _mean(under),
        "over_application_rate": _mean(over),
        "abstained_rate": _mean(abst),
        "mandatory_ecdd_recall": _mean([float(p.get("tier") == "enhanced") for g, p in det if g.mandatory_ecdd]),
        "macro_f1": _macro_f1(det),
        "confusion": {exp: dict(c) for exp, c in confusion.items()},
        "accuracy_by_customer_type": {t: {"n": len(v), "accuracy": _mean(v)} for t, v in sorted(by_type.items())},
    }

    # ------------------------------------------------------------ abstention
    unans = [(g, p) for g, p in pairs if not g.answerable]
    ans = [(g, p) for g, p in pairs if g.answerable]
    m["abstention"] = {
        "unanswerable_n": len(unans),
        "unanswerable_abstain_rate": _mean([float(bool(p.get("abstained"))) for _, p in unans]),
        "answerable_n": len(ans),
        "false_abstain_rate": _mean([float(bool(p.get("abstained"))) for _, p in ans]),
    }

    # ------------------------------------------------------------ retrieval + attribution
    recall, hit, rr, c_prec, c_prec_doc, c_rec = [], [], [], [], [], []
    unreachable: list[str] = []
    for g, p in ans:
        refs = reachable_refs(g, available_docs)
        if not refs:
            unreachable.append(g.id)
            continue
        retrieved = p.get("retrieved", [])[:k]
        found = [r for r in refs if any(ref_matches(cid, r) for cid in retrieved)]
        recall.append(len(found) / len(refs))
        hit.append(float(bool(found)))
        first = next((i for i, cid in enumerate(retrieved, 1) if any(ref_matches(cid, r) for r in refs)), None)
        rr.append(1.0 / first if first else 0.0)
        cited = p.get("cited", [])
        if cited and not p.get("abstained"):
            c_prec.append(sum(any(ref_matches(c, r) for r in refs) for c in cited) / len(cited))
            ref_docs = {_doc_of(r) for r in refs}
            c_prec_doc.append(sum(_doc_of(c) in ref_docs for c in cited) / len(cited))
            c_rec.append(sum(any(ref_matches(c, r) for c in cited) for r in refs) / len(refs))
    m["retrieval"] = {"n": len(recall), f"recall_at_{k}": _mean(recall), f"hit_at_{k}": _mean(hit),
                      "mrr": _mean(rr), "items_without_reachable_refs": unreachable}
    m["attribution"] = {
        "citation_validity": _mean([p.get("checks", {}).get("citation_validity", 1.0) for _, p in pairs
                                    if p.get("checks")]),
        "citation_precision_section": _mean(c_prec),
        "citation_precision_document": _mean(c_prec_doc),
        "citation_recall_section": _mean(c_rec),
        "answers_with_uncited_points": sum(1 for _, p in pairs if p.get("checks", {}).get("uncited_points")),
    }

    # ------------------------------------------------------------ faithfulness
    judged, lexical = [], []
    for _, p in pairs:
        if p.get("abstained"):
            continue
        for pt in p.get("points", []):
            lexical.append(float(bool(pt.get("supported_lexical"))))
            if pt.get("judge_supported") is not None:
                judged.append(float(bool(pt["judge_supported"])))
    m["faithfulness"] = {
        "points": len(lexical),
        "judge_supported_rate": _mean(judged),
        "lexical_supported_rate": _mean(lexical),
        "judge": preds and next(iter(preds.values())).get("judge_name"),
    }

    # ------------------------------------------------------------ explain effectiveness
    kf = [key_fact_recall(p.get("answer_text", ""), g.key_facts) for g, p in pairs
          if g.mode == "explain" and g.answerable and g.key_facts]
    m["explain"] = {"n": len(kf), "key_fact_recall": _mean([x for x in kf if x is not None])}

    # ------------------------------------------------------------ consistency across paraphrases / customer types
    groups: dict[str, list[tuple[GoldItem, dict]]] = defaultdict(list)
    for g, p in det:
        if g.group:
            groups[g.group].append((g, p))
    agree, correct = [], []
    detail = {}
    for name, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        tiers = [p.get("tier") for _, p in members]
        agree.append(float(len(set(tiers)) == 1))
        correct.append(float(all(t in g.acceptable for (g, _), t in zip(members, tiers))))
        detail[name] = {g.id: p.get("tier") for g, p in members}
    m["consistency"] = {"groups": len(agree), "agreement_rate": _mean(agree), "all_correct_rate": _mean(correct),
                        "detail": detail}

    # ------------------------------------------------------------ confidence calibration + ops
    calib: dict[str, list[float]] = defaultdict(list)
    for g, p in det:
        calib[p.get("confidence") or "none"].append(float((p.get("tier") or ABSTAIN) in g.acceptable))
    m["calibration"] = {c: {"n": len(v), "accuracy": _mean(v)} for c, v in sorted(calib.items())}
    lat = [p["latency_s"] for _, p in pairs if p.get("latency_s") is not None]
    m["latency_s"] = {"mean": round(statistics.mean(lat), 2) if lat else None, "p50": _percentile(lat, 0.5),
                      "p95": _percentile(lat, 0.95)}
    m["errors"] = [pid for pid, p in preds.items() if p.get("error")]
    m["needs_review_rate"] = _mean([float(bool(p.get("needs_review"))) for _, p in pairs])

    m["headline"] = headline(m)
    return m


def _macro_f1(det: list[tuple[GoldItem, dict]]) -> float | None:
    if not det:
        return None
    f1s = []
    for t in TIERS:
        tp = sum(1 for g, p in det if g.expected_tier == t and p.get("tier") == t)
        fp = sum(1 for g, p in det if g.expected_tier != t and p.get("tier") == t)
        fn = sum(1 for g, p in det if g.expected_tier == t and p.get("tier") != t)
        if tp + fp + fn == 0:
            continue
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return round(sum(f1s) / len(f1s), 4) if f1s else None


def headline(m: dict[str, Any]) -> dict[str, Any]:
    k = m["k"]
    faith = m["faithfulness"]["judge_supported_rate"]
    if faith is None:
        faith = m["faithfulness"]["lexical_supported_rate"]
    return {
        "tier_accuracy_acceptable": m["tier"]["accuracy_acceptable"],
        "tier_accuracy_strict": m["tier"]["accuracy_strict"],
        "mandatory_ecdd_recall": m["tier"]["mandatory_ecdd_recall"],
        "under_application_rate": m["tier"]["under_application_rate"],
        "over_application_rate": m["tier"]["over_application_rate"],
        "retrieval_recall_at_k": m["retrieval"][f"recall_at_{k}"],
        "citation_validity": m["attribution"]["citation_validity"],
        "citation_precision": m["attribution"]["citation_precision_section"],
        "citation_recall": m["attribution"]["citation_recall_section"],
        "faithfulness": faith,
        "key_fact_recall": m["explain"]["key_fact_recall"],
        "unanswerable_abstain_rate": m["abstention"]["unanswerable_abstain_rate"],
        "false_abstain_rate": m["abstention"]["false_abstain_rate"],
        "consistency_agreement": m["consistency"]["agreement_rate"],
        "latency_p50_s": m["latency_s"]["p50"],
        "latency_p95_s": m["latency_s"]["p95"],
    }


# name -> (headline key, direction)
THRESHOLD_KEYS = {
    "tier_accuracy_acceptable": ("tier_accuracy_acceptable", "min"),
    "mandatory_ecdd_recall": ("mandatory_ecdd_recall", "min"),
    "under_application_rate_max": ("under_application_rate", "max"),
    "retrieval_recall_at_k": ("retrieval_recall_at_k", "min"),
    "citation_validity": ("citation_validity", "min"),
    "citation_precision": ("citation_precision", "min"),
    "faithfulness": ("faithfulness", "min"),
    "unanswerable_abstain_rate": ("unanswerable_abstain_rate", "min"),
    "false_abstain_rate_max": ("false_abstain_rate", "max"),
}


def check_thresholds(head: dict[str, Any], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    out = []
    for name, limit in thresholds.items():
        key, direction = THRESHOLD_KEYS.get(name, (name, "min"))
        value = head.get(key)
        passed = value is not None and (value >= limit if direction == "min" else value <= limit)
        out.append({"name": name, "metric": key, "value": value, "limit": limit, "direction": direction,
                    "passed": passed})
    return out
