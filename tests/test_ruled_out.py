"""Prompt v3.2: facts the scenario rules out, required vs risk-based measures, citation checks."""
from pathlib import Path

from amlrag.eval.gold import load_gold
from amlrag.generate.prompts import DETERMINE_SCHEMA, DETERMINE_SYSTEM, PROMPT_VERSION, determine_messages
from amlrag.generate.verify import verify
from amlrag.pipeline import DETERMINE_GROUPS, ruled_out_called_unknown
from amlrag.retrieve.facts import mentions_fact, normalise_facts, tristate


def test_facts_are_yes_no_unknown():
    f = normalise_facts({"customer_type": "company", "pep_status": "none", "high_risk_jurisdiction": "no",
                         "unusual_transaction": "unknown", "suspicious_matter_continuing": "yes"})
    assert f["high_risk_jurisdiction"] is False and f["suspicious_matter_continuing"] is True
    assert f["ruled_out"] == ["pep", "high_risk_jurisdiction"]          # unknown is not ruled out
    assert tristate(False) == "unknown" and tristate("No") == "no" and tristate(True) == "yes"
    # Booleans (older answers, the offline stub) can't say "denied", so they never rule a fact out.
    assert normalise_facts({"high_risk_jurisdiction": False})["ruled_out"] == []


def test_ruled_out_facts_reach_the_prompt_as_established():
    f = normalise_facts({"customer_type": "company", "pep_status": "unknown", "high_risk_jurisdiction": "no"})
    user = determine_messages("A company.", [], f)[0][1]["content"]
    assert "Ruled out by the scenario (established as false, not missing)" in user
    assert "FATF call-for-action country" in user
    assert "Never say the scenario does not state it" in DETERMINE_SYSTEM
    assert '"regardless"' in DETERMINE_SYSTEM and PROMPT_VERSION == "3.2"


def test_answer_calling_a_ruled_out_fact_unknown_is_flagged_not_removed():
    facts = normalise_facts({"high_risk_jurisdiction": "no"})
    missing = ["Whether any beneficial owner is physically located in the high-risk jurisdiction",
               "The customer's ML/TF risk rating"]
    texts = ["The scenario does not state whether the beneficial owners are located in that country.",
             "The beneficial owners are not located in that country, so the trigger is not met."]
    hits = ruled_out_called_unknown(facts, texts, missing)
    assert hits == [missing[0], texts[0]]
    assert ruled_out_called_unknown(normalise_facts({}), texts, missing) == []
    assert mentions_fact("Is anyone a politically exposed person?", "pep")
    assert not mentions_fact("Payments go to suppliers abroad", "high_risk_jurisdiction")


def test_measures_carry_required_or_risk_based(assistant):
    item = DETERMINE_SCHEMA["properties"]["required_measures"]["items"]
    assert "required" in item["required"]
    _, label_map = determine_messages("x", assistant.retriever.search("enhanced customer due diligence"), None)
    out = {"reasoning": [], "required_measures": [
        {"measure": "Establish source of funds", "required": False, "sources": ["S1"]},
        {"measure": "Senior manager approval", "required": True, "sources": ["S1"]},
        {"measure": "Collect KYC", "sources": ["S1"]}]}
    pts = verify(out, label_map, 0.0, DETERMINE_GROUPS).points["required_measures"]
    assert [p.required for p in pts] == [False, True, None]
    assert pts[0].to_dict(label_map)["required"] is False


def test_answer_reports_separate_citation_checks(assistant):
    r = assistant.determine("A foreign politically exposed person opens a personal account.")
    c = r["checks"]
    assert {"citation_validity", "supported_points", "ruled_out_called_unknown",
            "required_measures", "optional_measures"} <= set(c)
    assert 0 <= c["supported_points"] <= c["points"]


def test_adversarial_set_loads():
    path = Path(__file__).resolve().parents[1] / "data" / "gold" / "adversarial.jsonl"
    items = {i.id: i for i in load_gold(path)}
    assert set(items) == {"A01-payments-only-ruled-out", "A02-grey-list-not-call-for-action",
                          "A03-call-for-action-measures-risk-based", "A04-payments-only-unknown"}
    assert items["A03-call-for-action-measures-risk-based"].mandatory_ecdd
    assert "enhanced" not in items["A01-payments-only-ruled-out"].acceptable


def test_adversarial_run_reports_answer_checks(built_cfg, tmp_path):
    from amlrag.eval.runner import run_eval

    path = Path(__file__).resolve().parents[1] / "data" / "gold" / "adversarial.jsonl"
    out_dir, metrics = run_eval(built_cfg, gold_path=str(path), verbose=False, out_dir=tmp_path / "adv")
    assert metrics["n_items"] == 4
    assert "answers_calling_ruled_out_fact_unknown" in metrics["attribution"]
    assert "## Answer checks" in (out_dir / "report.md").read_text()
