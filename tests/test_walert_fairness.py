"""Walert-comparable measures (graded NDCG, ROUGE-1, BERTScore, % unanswered) and counterfactual fairness."""
import math
import sys
import types

import pytest

from amlrag.eval.gold import GoldItem, load_gold
from amlrag.eval.metrics import compute_metrics, ndcg_at
from amlrag.eval.textmetrics import rouge1, rouge_tokens


def test_ndcg_perfect_and_graded():
    grades = {"rules2025::6-23": 2, "austrac-ecdd": 1}
    assert ndcg_at(["rules2025::6-23::0", "austrac-ecdd::x::0"], grades, 5) == pytest.approx(1.0)
    # Swapping the order puts the partially relevant item first.
    swapped = ndcg_at(["austrac-ecdd::x::0", "rules2025::6-23::0"], grades, 5)
    ideal = 2 / math.log2(2) + 1 / math.log2(3)
    assert swapped == pytest.approx((1 / math.log2(2) + 2 / math.log2(3)) / ideal)
    assert ndcg_at(["other::a::0"], grades, 5) == 0.0
    assert ndcg_at([], {}, 5) is None


def test_ndcg_credits_each_reference_once():
    # Three chunks of the same relevant document must not all earn credit.
    grades = {"austrac-ecdd": 2, "rules2025::6-23": 2}
    many = ndcg_at(["austrac-ecdd::a::0", "austrac-ecdd::b::0", "austrac-ecdd::c::0"], grades, 3)
    assert many == pytest.approx((2 / math.log2(2)) / (2 / math.log2(2) + 2 / math.log2(3)))


def test_ndcg_cutoff():
    grades = {"a": 2}
    assert ndcg_at(["x::0", "x::1", "a::0"], grades, 1) == 0.0
    assert ndcg_at(["x::0", "x::1", "a::0"], grades, 3) == pytest.approx(1 / math.log2(4))


def test_rouge_tokens_match_rouge_score_conventions():
    assert rouge_tokens("Source-of-wealth (SoW), rule 6-23!") == ["source", "of", "wealth", "sow", "rule", "6", "23"]
    r = rouge1("the cat sat", "the cat")
    assert r["precision"] == pytest.approx(2 / 3) and r["recall"] == 1.0
    assert rouge1("", "x") == {"precision": 0.0, "recall": 0.0, "f1": 0.0}


def _g(id, **kw):
    base = dict(mode="determine", query=f"q {id}", expected_tier="standard", acceptable_tiers=["standard"],
                expected_sections=["rules2025::6-1"], reference_answer="Standard CDD applies.", answer_type="known")
    base.update(kw)
    return GoldItem(id=id, **base)


def test_walert_block_and_variants_excluded_from_headline():
    items = [
        _g("a", partial_sections=["austrac-x"]),
        _g("a2", counterfactual_of="a", tags=["fairness"]),
        _g("a3", counterfactual_of="a", tags=["fairness"]),
        _g("b", answer_type="inferred", expected_tier="enhanced", acceptable_tiers=["enhanced"],
           reference_answer="Enhanced CDD for a foreign PEP."),
        _g("u", mode="explain", expected_tier=None, acceptable_tiers=[], answerable=False, answer_type="out_of_kb",
           expected_sections=[], reference_answer=""),
        _g("u2", mode="explain", expected_tier=None, acceptable_tiers=[], answerable=False, answer_type="out_of_kb",
           expected_sections=[], reference_answer=""),
    ]
    preds = {
        "a": {"tier": "standard", "retrieved": ["rules2025::6-1::0"], "answer_text": "Standard CDD applies.",
              "confidence": "medium", "bertscore": {"precision": 0.9, "recall": 0.8, "f1": 0.85}},
        "a2": {"tier": "standard", "confidence": "medium", "answer_text": "Standard CDD applies."},
        "a3": {"tier": "enhanced", "confidence": "high", "answer_text": "Enhanced."},             # a flip
        "b": {"tier": "enhanced", "retrieved": ["x::0", "rules2025::6-1::0"], "answer_text": "Enhanced CDD.",
              "confidence": "high", "bertscore": {"precision": 0.7, "recall": 0.6, "f1": 0.65}},
        "u": {"abstained": True}, "u2": {"abstained": False},
    }
    m = compute_metrics(items, preds, {"rules2025", "austrac-x"}, 8)
    assert m["n_items"] == 4 and m["n_counterfactual_variants"] == 2
    assert m["tier"]["n"] == 2 and m["tier"]["accuracy_acceptable"] == 1.0   # the flipped variant doesn't count here
    w = m["walert"]
    assert w["out_of_kb_n"] == 2 and w["pct_unanswered_out_of_kb"] == 0.5
    assert w["ndcg"]["known"]["n"] == 1 and w["ndcg"]["inferred"]["@1"] == 0.0
    assert w["ndcg"]["known"]["@1"] == pytest.approx(2 / 2)                      # top chunk is the grade-2 section
    assert w["rouge1"]["n"] == 2 and w["rouge1"]["f1"] is not None
    assert w["bertscore"]["f1"] == pytest.approx(0.75)
    f = m["fairness"]
    assert f["groups"] == 1 and f["variants"] == 2
    assert f["tier_flip_rate"] == 0.5 and f["invariance_rate"] == 0.0 and f["confidence_flip_rate"] == 0.5
    assert f["flips"] == [{"id": "a3", "base": "a", "base_tier": "standard", "tier": "enhanced"}]
    assert m["headline"]["fairness_tier_flip_rate"] == 0.5
    assert m["headline"]["walert_pct_unanswered_out_of_kb"] == 0.5


def test_fairness_threshold_is_checked():
    from amlrag.eval.metrics import check_thresholds

    res = check_thresholds({"fairness_tier_flip_rate": 0.1}, {"fairness_tier_flip_rate_max": 0.0})
    assert res[0]["passed"] is False and res[0]["direction"] == "max"


def test_counterfactual_validation(tmp_path):
    import json

    def row(**kw):
        d = dict(id="x", mode="determine", query="q", answerable=True, expected_tier="standard",
                 acceptable_tiers=["standard"], expected_sections=["a"], reference_answer="r", answer_type="known")
        d.update(kw)
        return json.dumps(d)

    path = tmp_path / "g.jsonl"
    path.write_text("\n".join([row(id="base"), row(id="v", query="q2", counterfactual_of="base",
                                                   expected_tier="enhanced", acceptable_tiers=["enhanced"]),
                               row(id="w", query="q3", counterfactual_of="missing")]))
    with pytest.raises(ValueError) as exc:
        load_gold(path)
    msg = str(exc.value)
    assert "must expect the same answer" in msg and "'missing' does not exist" in msg


def test_gold_needs_reference_answer_and_valid_answer_type():
    from amlrag.eval.gold import validate

    errs = " ".join(validate(_g("z", reference_answer="", answer_type="sometimes")))
    assert "reference_answer" in errs and "answer_type" in errs
    errs = " ".join(validate(_g("z", answer_type="out_of_kb")))
    assert "requires answerable: false" in errs


def test_bertscore_used_when_installed(built_cfg, monkeypatch):
    """bert-score is heavy (PyTorch + roberta-large); a fake module checks the wiring."""
    calls = {}

    class _T(list):
        def tolist(self):
            return list(self)

    def fake_score(cands, refs, model_type=None, lang=None, rescale_with_baseline=False, batch_size=16, verbose=False):
        calls.update(n=len(cands), model_type=model_type, rescale=rescale_with_baseline)
        return _T([0.9] * len(cands)), _T([0.8] * len(cands)), _T([0.85] * len(cands))

    monkeypatch.setitem(sys.modules, "bert_score", types.SimpleNamespace(score=fake_score))
    monkeypatch.setattr("amlrag.eval.runner.bertscore_available", lambda: True)
    from amlrag.eval.runner import run_eval

    _, m = run_eval(built_cfg, verbose=False)
    assert calls["model_type"] == "roberta-large" and calls["n"] > 0
    assert m["walert"]["bertscore"]["f1"] == pytest.approx(0.85)
    assert m["run"]["bertscore"]["status"].startswith("computed")


def test_bertscore_skipped_when_missing(built_cfg, monkeypatch):
    monkeypatch.setattr("amlrag.eval.runner.bertscore_available", lambda: False)
    from amlrag.eval.runner import run_eval

    _, m = run_eval(built_cfg, verbose=False)
    assert m["walert"]["bertscore"] is None and "not installed" in m["run"]["bertscore"]["status"]
    with pytest.raises(RuntimeError, match="bert-score is not installed"):
        run_eval(built_cfg.override("eval.bertscore", {"enabled": True}), verbose=False)


def test_tag_filter_keeps_counterfactual_bases(built_cfg):
    from amlrag.eval.runner import run_eval

    _, m = run_eval(built_cfg, verbose=False, tags=["fairness"])
    assert m["run"]["n_items"] == 2 and m["fairness"]["groups"] == 1
