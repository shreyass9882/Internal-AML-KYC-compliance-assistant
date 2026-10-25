"""Prompt v3.3: an ML/TF risk rating counts only when the scenario states it; a measure stays
"required" only when its cited source uses mandatory wording. Found by adversarial test A05."""
import json
from pathlib import Path

import pytest

from amlrag.eval.gold import load_gold
from amlrag.generate.guardrails import apply_guardrails
from amlrag.generate.prompts import _facts_lines
from amlrag.generate.verify import VerifiedPoint, enforce_required_wording
from amlrag.models import Chunk, Retrieved
from amlrag.retrieve.facts import extract_facts, risk_rating_stated

A05 = ("A customer regularly sends payments to suppliers in a FATF high-risk jurisdiction. The customer, beneficial "
       "owners, persons acting on its behalf, and persons on whose behalf it receives the service are all explicitly "
       "stated not to be physically present in or formed in that jurisdiction. No other ECDD trigger is identified. "
       "Should the customer automatically receive Enhanced CDD?")


@pytest.mark.parametrize("text", [
    "Risk rating medium; no PEP or sanctions matches.", "Medium risk, no PEP matches.", "Risk is low.",
    "We rate the ML/TF risk as low.", "Our risk methodology rates the customer as high ML/TF risk.",
    "previously rated low risk", "We would rate it medium risk", "a low-risk customer", "risk rating: high",
])
def test_stated_ratings_are_found(text):
    assert risk_rating_stated(text)


@pytest.mark.parametrize("text", [
    A05, "suppliers in a FATF high-risk jurisdiction", "located in a high risk country",
    "no other identified high-risk characteristics", "No other ECDD trigger is identified.",
    "We assessed the customer, who lives in a high-risk country",
])
def test_risky_things_are_not_ratings(text):
    assert not risk_rating_stated(text)


def test_every_rating_in_the_gold_set_is_found():
    """A rating the detector missed would be thrown away, so check the project's own scenarios."""
    root = Path(__file__).resolve().parents[1] / "data" / "gold"
    for item in load_gold(root / "scenarios.jsonl"):
        q = item.query.lower()
        if item.mode == "determine" and ("rate" in q and " risk" in q or "risk rating" in q or "risk is" in q):
            assert risk_rating_stated(item.query), item.id


class FactsLLM:
    """Stands in for the fact-extraction model and returns a fixed rating."""
    def __init__(self, rating):
        self.rating = rating

    def chat_json(self, messages, schema, task=""):
        return {"customer_type": "company", "pep_status": "none", "high_risk_jurisdiction": "no",
                "ml_tf_risk": self.rating, "missing_information": []}, {}


def test_unstated_rating_is_ignored_and_the_guardrail_stays_quiet():
    facts, _ = extract_facts(FactsLLM("high"), A05)
    assert facts["ml_tf_risk"] == "unknown" and facts["risk_rating_stated"] is False
    assert "high_risk_jurisdiction" in facts["ruled_out"]
    guard = apply_guardrails("standard", facts, {})
    assert guard["tier"] == "standard" and not guard["escalated"] and "high_risk" not in guard["fired"]
    assert "not stated in the scenario" in _facts_lines(facts)


def test_stated_rating_is_kept():
    facts, _ = extract_facts(FactsLLM("high"), "A sole trader. Our methodology rates the customer as high ML/TF risk.")
    assert facts["ml_tf_risk"] == "high" and facts["risk_rating_stated"] is True
    assert "not stated in the scenario" not in _facts_lines(facts)


def _source(label, text):
    c = Chunk(chunk_id=f"doc::{label}::0", doc_id="doc", section_key=label, citation=label, heading_path=label,
              text=text, url=None, kind="guidance", position=0, word_count=len(text.split()))
    return Retrieved(chunk=c)


def test_measures_from_an_examples_list_are_not_required():
    label_map = {
        "S8": _source("S8", "For example, it may be appropriate to apply one or more of the following enhanced CDD "
                            "measures: collecting more KYC information; obtaining the source of funds."),
        "S7": _source("S7", "You must conduct enhanced CDD if the customer's ML/TF risk is high."),
    }
    example = VerifiedPoint("Collect more KYC information", ["S8"], [], 1.0, True, None, True)
    mandatory = VerifiedPoint("Conduct enhanced CDD", ["S7"], [], 1.0, True, None, True)
    optional = VerifiedPoint("Obtain the source of funds", ["S8"], [], 1.0, True, None, False)
    assert enforce_required_wording([example, mandatory, optional], label_map) == 1
    assert example.required is False and mandatory.required is True and optional.required is False


def test_a05_is_in_the_adversarial_set():
    root = Path(__file__).resolve().parents[1] / "data" / "gold"
    items = {i.id: i for i in load_gold(root / "adversarial.jsonl")}
    a05 = items["A05-payments-only-no-other-trigger"]
    assert a05.query == A05 and a05.expected_tier == "standard" and not a05.mandatory_ecdd


def test_enhanced_without_any_basis_is_flagged_for_review():
    from amlrag.pipeline import unsupported_enhanced

    facts, _ = extract_facts(FactsLLM("high"), A05)            # rating ignored, jurisdiction ruled out
    assert unsupported_enhanced("enhanced", [], facts)
    assert not unsupported_enhanced("standard", [], facts)
    assert not unsupported_enhanced("enhanced", ["foreign_pep"], facts)   # a real trigger fired
    stated, _ = extract_facts(FactsLLM("high"), "A company. We rate it as high risk.")
    assert not unsupported_enhanced("enhanced", [], stated)              # a stated high rating
