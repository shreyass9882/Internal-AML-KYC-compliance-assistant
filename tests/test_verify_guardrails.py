from amlrag.generate.guardrails import apply_guardrails
from amlrag.generate.verify import cap_confidence, lexical_support, normalise_label, verify
from amlrag.models import Chunk, Retrieved


def _r(cid, text, heading="h"):
    return Retrieved(Chunk(cid, cid.split("::")[0], "s", f"Cite {cid}", heading, text, None, "legislation", 0,
                           len(text.split())))


LABELS = {
    "S1": _r("rules2025::6-23::0", "If the customer is a foreign politically exposed person the reporting entity "
                                   "must establish the source of wealth and source of funds."),
    "S2": _r("austrac-ecdd::when::0", "You must apply enhanced customer due diligence if the customer is connected "
                                      "to a high-risk jurisdiction subject to a FATF call for action."),
    "S3": _r("rules2025::6-18::0", "Simplified customer due diligence for beneficial owners of government bodies."),
}


def test_normalise_label_variants():
    assert normalise_label("S2") == "S2"
    assert normalise_label("[s3]") == "S3"
    assert normalise_label("Source 4") == "S4"
    assert normalise_label("rule 6-23") is None


def test_lexical_support():
    assert lexical_support("establish the source of wealth", [LABELS["S1"].chunk.text]) == 1.0
    assert lexical_support("the moon is made of cheese", [LABELS["S1"].chunk.text]) == 0.0


def test_verify_flags_invalid_and_uncited_points():
    out = {"reasoning": [
        {"point": "A foreign politically exposed person requires source of wealth checks.", "sources": ["S1"]},
        {"point": "Invented rule about unicorns.", "sources": ["S9"]},
        {"point": "No citation here.", "sources": []},
    ], "required_measures": [{"measure": "Establish source of funds.", "sources": "S1, S2"}]}
    ver = verify(out, LABELS, 0.3, {"reasoning": "point", "required_measures": "measure"})
    pts = ver.all_points
    assert pts[0].supported and pts[0].labels == ["S1"]
    assert pts[1].invalid_labels == ["S9"] and not pts[1].supported
    assert len(ver.uncited) == 2
    assert ver.total_labels == 4 and ver.valid_labels == 3
    assert ver.cited_labels == ["S1", "S2"]
    conf, notes = cap_confidence("high", ver, 0.34)
    assert conf == "low" and notes


def test_cap_confidence_never_raises():
    out = {"reasoning": [{"point": "source of wealth and source of funds", "sources": ["S1"]}]}
    ver = verify(out, LABELS, 0.3, {"reasoning": "point"})
    assert cap_confidence("medium", ver, 0.34)[0] == "medium"
    assert cap_confidence("high", ver, 0.34)[0] == "high"
    assert cap_confidence("nonsense", ver, 0.34)[0] == "low"


FACTS_FPEP = {"pep_status": "foreign", "pep_same_country_foreign_branch": False, "ml_tf_risk": "medium"}


def test_guardrail_escalates_missed_foreign_pep_with_citation():
    g = apply_guardrails("standard", FACTS_FPEP, LABELS, "escalate")
    assert g["tier"] == "enhanced" and g["escalated"] and g["fired"] == ["foreign_pep"]
    assert g["added_points"][0]["sources"] == ["S1"]


def test_guardrail_flag_mode_keeps_tier():
    g = apply_guardrails("standard", FACTS_FPEP, LABELS, "flag")
    assert g["tier"] == "standard" and not g["escalated"] and g["warnings"]


def test_guardrail_does_not_escalate_without_evidence():
    only_simplified = {"S3": LABELS["S3"]}
    g = apply_guardrails("simplified", {**FACTS_FPEP, "ml_tf_risk": "low"}, only_simplified, "escalate")
    assert g["tier"] == "simplified" and "knowledge base may be missing" in g["warnings"][0]


def test_guardrail_foreign_branch_exception():
    g = apply_guardrails("standard", {**FACTS_FPEP, "pep_same_country_foreign_branch": True}, LABELS, "escalate")
    assert g["tier"] == "standard" and not g["fired"]


def test_guardrail_simplified_with_medium_risk_moves_to_standard():
    g = apply_guardrails("simplified", {"pep_status": "none", "ml_tf_risk": "medium"}, LABELS, "escalate")
    assert g["tier"] == "standard" and g["warnings"]


def test_guardrail_noop_without_facts_or_when_enhanced():
    assert apply_guardrails("standard", None, LABELS)["tier"] == "standard"
    assert apply_guardrails("enhanced", FACTS_FPEP, LABELS)["warnings"] == []
