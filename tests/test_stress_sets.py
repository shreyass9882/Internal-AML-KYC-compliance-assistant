"""The retrieval stress set (data/gold/retrieval-stress.jsonl, added 5 October 2026) and the references
of both extra test files: every reference must point at passages that are really in the knowledge base,
or Recall@k and citation precision would be scored against something the retriever can never find."""
import json
from pathlib import Path

import pytest

from amlrag.eval.gold import load_gold
from amlrag.models import ref_matches

REPO = Path(__file__).resolve().parents[1]
GOLD = REPO / "data" / "gold"
CHUNKS = REPO / "kb" / "processed" / "chunks.jsonl"


def test_retrieval_stress_set_loads():
    items = load_gold(GOLD / "retrieval-stress.jsonl")
    assert [i.id[:3] for i in items] == [f"R0{n}" for n in range(1, 9)]
    for i in items:
        assert i.mode == "explain" and i.answerable and i.expected_sections and i.key_facts
        assert i.category in ("known", "inferred") and i.reference_answer
        for ref in i.expected_sections + i.partial_sections:
            assert ref.count("::") <= 1 and ref.strip() == ref


@pytest.mark.skipif(not CHUNKS.exists(), reason="knowledge base not built")
@pytest.mark.parametrize("name", ["retrieval-stress.jsonl", "adversarial.jsonl"])
def test_every_reference_is_in_the_knowledge_base(name):
    chunk_ids = [json.loads(line)["chunk_id"] for line in CHUNKS.read_text(encoding="utf-8").splitlines() if line]
    missing = [(i.id, ref) for i in load_gold(GOLD / name)
               for ref in i.expected_sections + i.partial_sections
               if not any(ref_matches(c, ref) for c in chunk_ids)]
    assert not missing, missing


def test_retrieval_stress_run_scores_retrieval(built_cfg, tmp_path, capsys):
    from amlrag.eval import items
    from amlrag.eval.runner import run_eval

    gold = GOLD / "retrieval-stress.jsonl"
    out_dir, metrics = run_eval(built_cfg, gold_path=str(gold), verbose=False, out_dir=tmp_path / "stress")
    assert metrics["n_items"] == 8 and metrics["explain"]["n"] == 8
    assert "mrr" in metrics["retrieval"] and "citation_precision_section" in metrics["attribution"]
    # The per-item table: one row per question, written next to report.md.
    assert items.main([str(out_dir), "--gold", str(gold)]) == 0
    table = (out_dir / "items.md").read_text(encoding="utf-8")
    assert all(f"R0{n}-" in table for n in range(1, 9)) and "of 8 passed" in capsys.readouterr().out


def test_item_rows_score_each_kind_of_item():
    from amlrag.eval.items import item_row

    adv = {i.id: i for i in load_gold(GOLD / "adversarial.jsonl")}
    ret = {i.id: i for i in load_gold(GOLD / "retrieval-stress.jsonl")}
    # Determine: a tier inside acceptable_tiers passes; enhanced on A06 fails.
    assert item_row(adv["A06-customer-known-no-other-trigger-info"], {"tier": "standard"})["ok"]
    assert not item_row(adv["A06-customer-known-no-other-trigger-info"], {"tier": "enhanced"})["ok"]
    # Unanswerable: only declining passes, for the contradiction and the out-of-scope question alike.
    assert item_row(adv["A07-contradictory-beneficial-owner-location"],
                    {"tier": "insufficient_information", "abstained": True})["ok"]
    r = item_row(adv["A08-smr-deadline-out-of-kb"], {"abstained": False, "answer_text": "Within 24 hours."})
    assert not r["ok"] and r["result"] == "answered"
    # Explain: retrieval rank, key facts and citation precision come from the saved prediction.
    g = ret["R08-pep-matters"]
    r = item_row(g, {"abstained": False,
                     "answer_text": "Establish whether the customer or a beneficial owner is a PEP.",
                     "retrieved": ["austrac-ecdd::introduction::0", "rules2025::6-23::0"],
                     "cited": ["rules2025::6-23::0", "austrac-ecdd::introduction::0"]})
    assert r["found"] == 1 and r["first"] == 2 and r["precision"] == 0.5
    assert "on whose behalf" in r["missing"] and "beneficial owner" not in r["missing"]
    assert not r["ok"]                                   # answered, but with 1 of 6 key facts
    full = item_row(g, {"abstained": False, "answer_text": g.reference_answer, "retrieved": ["rules2025::6-23::0"]})
    assert full["ok"] and full["facts"] == 1.0 and not full["missing"]
    assert not item_row(g, {"abstained": False, "answer_text": g.reference_answer, "retrieved": []})["ok"]
