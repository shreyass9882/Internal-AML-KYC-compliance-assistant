import json
from pathlib import Path

import pytest

from amlrag.eval.gold import GoldItem, load_gold, validate
from amlrag.eval.metrics import check_thresholds, compute_metrics, key_fact_recall

REPO = Path(__file__).resolve().parents[1]


def _g(id, tier, acceptable=None, mandatory=False, answerable=True, mode="determine", **kw):
    return GoldItem(id=id, mode=mode, query="q", answerable=answerable, expected_tier=tier,
                    acceptable_tiers=acceptable or ([tier] if tier else []), mandatory_ecdd=mandatory,
                    expected_sections=kw.pop("sections", ["rules2025::6-23"]) if answerable else [], **kw)


def test_tier_metrics_under_and_over_application():
    items = [_g("a", "enhanced", mandatory=True), _g("b", "enhanced", mandatory=True),
             _g("c", "standard"), _g("d", "simplified", ["simplified", "standard"]),
             _g("e", "insufficient_information", answerable=False)]
    preds = {
        "a": {"tier": "enhanced", "retrieved": ["rules2025::6-23::0"], "cited": ["rules2025::6-23::0"]},
        "b": {"tier": "standard", "retrieved": ["x::1::0", "rules2025::6-23::0"], "cited": ["x::1::0"]},  # under
        "c": {"tier": "enhanced", "retrieved": [], "cited": []},                                          # over
        "d": {"tier": "standard", "retrieved": ["rules2025::6-23::1"], "cited": []},                       # acceptable
        "e": {"tier": "insufficient_information", "abstained": True},
    }
    m = compute_metrics(items, preds, {"rules2025", "x"}, k=8)
    t = m["tier"]
    assert t["accuracy_acceptable"] == 0.5 and t["accuracy_strict"] == 0.25
    assert t["under_application_rate"] == 0.25 and t["over_application_rate"] == 0.25
    assert t["mandatory_ecdd_recall"] == 0.5
    assert t["confusion"]["enhanced"] == {"enhanced": 1, "standard": 1}
    assert m["abstention"]["unanswerable_abstain_rate"] == 1.0 and m["abstention"]["false_abstain_rate"] == 0.0
    r = m["retrieval"]
    assert r["recall_at_8"] == 0.75 and r["mrr"] == pytest.approx((1 + 0.5 + 0 + 1) / 4)
    assert m["attribution"]["citation_precision_section"] == 0.5  # a: 1.0, b: 0.0


def test_unreachable_refs_are_skipped():
    items = [_g("a", "enhanced", sections=["amlctf-act::32"])]
    m = compute_metrics(items, {"a": {"tier": "enhanced", "retrieved": []}}, {"rules2025"}, 8)
    assert m["retrieval"]["n"] == 0 and m["retrieval"]["items_without_reachable_refs"] == ["a"]


def test_consistency_groups():
    items = [_g("a", "enhanced", group="G"), _g("b", "enhanced", group="G"), _g("c", "standard", group="H"),
             _g("d", "standard", group="H")]
    preds = {"a": {"tier": "enhanced"}, "b": {"tier": "enhanced"}, "c": {"tier": "standard"}, "d": {"tier": "enhanced"}}
    c = compute_metrics(items, preds, set(), 8)["consistency"]
    assert c["groups"] == 2 and c["agreement_rate"] == 0.5 and c["all_correct_rate"] == 0.5


def test_key_fact_recall_alternatives():
    assert key_fact_recall("Source of wealth is overall wealth.", [["source of wealth"], ["overall", "total"]]) == 1.0
    assert key_fact_recall("nothing", [["a"], ["b"]]) == 0.0
    assert key_fact_recall("x", []) is None


def test_thresholds_directions():
    res = {r["name"]: r["passed"] for r in check_thresholds(
        {"tier_accuracy_acceptable": 0.9, "under_application_rate": 0.1},
        {"tier_accuracy_acceptable": 0.8, "under_application_rate_max": 0.05, "faithfulness": 0.8})}
    assert res == {"tier_accuracy_acceptable": True, "under_application_rate_max": False, "faithfulness": False}


def test_project_gold_set_is_valid_and_consistent():
    from collections import Counter

    items = load_gold(REPO / "data" / "gold" / "scenarios.jsonl")
    base = [i for i in items if not i.is_variant]
    det = [i for i in base if i.mode == "determine"]
    scenarios = [i for i in det if i.answerable]
    assert len(scenarios) >= 35, "Milestone 1 plan: 35-40 customer scenarios"
    assert {i.expected_tier for i in det} >= {"simplified", "standard", "enhanced", "insufficient_information"}
    types = Counter(i.customer_type for i in scenarios)
    thin = {t: n for t, n in types.items() if t != "other" and n < 3}
    assert not thin, f"customer types with fewer than 3 scenarios: {thin}"
    assert sum(i.category == "out_of_kb" for i in base) >= 5          # Walert's % unanswered needs enough items
    assert sum(i.is_variant for i in items) >= 12
    groups = {}
    for i in det:
        if i.group:
            groups.setdefault(i.group, set()).add(i.expected_tier)
    assert all(len(v) == 1 for v in groups.values()), "items in a consistency group must share the expected tier"
    for i in items:
        for ref in i.expected_sections + i.partial_sections:
            assert ref.count("::") <= 1 and ref.strip() == ref
        if i.answerable:
            assert i.category in ("known", "inferred") and i.reference_answer


def test_gold_validation_catches_mistakes():
    bad = GoldItem(id="x", mode="determine", query="q", expected_tier="enhanced", acceptable_tiers=["standard"],
                   mandatory_ecdd=True, expected_sections=[])
    errs = " ".join(validate(bad))
    assert "expected_tier must be in acceptable_tiers" in errs and "expected_sections" in errs


def test_offline_eval_run_writes_outputs(built_cfg):
    from amlrag.eval.runner import run_eval

    out, m = run_eval(built_cfg, verbose=False)
    assert (out / "predictions.jsonl").exists() and (out / "report.md").exists()
    saved = json.loads((out / "metrics.json").read_text())
    assert saved["headline"]["mandatory_ecdd_recall"] == 1.0
    assert saved["run"]["generator"] == "stub"
    assert "Acceptance thresholds" in (out / "report.md").read_text()


def test_presets_toggle_components(built_cfg):
    from amlrag.eval.runner import apply_preset

    base = apply_preset(built_cfg, "baseline")
    assert base.retrieval.use_hybrid is False and base.verification.guardrails is False
    assert apply_preset(built_cfg, "full").verification.guardrails is True
    with pytest.raises(ValueError):
        apply_preset(built_cfg, "nope")
