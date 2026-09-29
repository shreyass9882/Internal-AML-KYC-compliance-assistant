"""End-to-end pipeline behaviour with scripted model outputs (no Ollama needed)."""
from amlrag import ABSTAIN
from amlrag.pipeline import Assistant


class ScriptedLLM:
    """Returns canned JSON per task and records the prompts it received."""

    name = "scripted"

    def __init__(self, facts=None, answer=None, fail=False):
        self.facts = facts or {}
        self.answer = answer or {}
        self.fail = fail
        self.calls = []

    def chat_json(self, messages, schema=None, task=""):
        self.calls.append((task, messages))
        if self.fail and task != "facts":
            raise RuntimeError("model crashed")
        return (self.facts if task == "facts" else self.answer), {"latency_s": 0.0}


def _assistant(cfg, llm, **overrides):
    for k, v in overrides.items():
        cfg = cfg.override(k, v)
    base = Assistant.from_config(cfg)
    return Assistant(cfg, base.retriever, llm, base.embedder_name, base.snapshot)


FPEP_FACTS = {"customer_type": "individual", "pep_status": "foreign", "pep_same_country_foreign_branch": False,
              "high_risk_jurisdiction": False, "suspicious_matter_continuing": False, "nested_services": False,
              "unusual_transaction": False, "virtual_assets_with_cash": False, "regulated_or_government": False,
              "ml_tf_risk": "medium", "delayed_verification": False, "missing_information": []}
SCENARIO = "An individual customer is a serving minister in a foreign government and opens an account."


def test_determine_returns_cited_answer(built_cfg):
    llm = ScriptedLLM(FPEP_FACTS, {"tier": "enhanced", "summary": "Enhanced CDD applies.",
                                   "reasoning": [{"point": "A foreign politically exposed person requires source of "
                                                           "wealth and source of funds.", "sources": ["S1"]}],
                                   "required_measures": [], "missing_information": [], "confidence": "high"})
    r = _assistant(built_cfg, llm).determine(SCENARIO)
    assert r["tier"] == "enhanced" and not r["abstained"]
    assert r["points"][0]["citations"][0]["label"] == "S1"
    assert r["sources"][0]["cited"] is True
    assert r["checks"]["citation_validity"] == 1.0
    # The facts step ran and its sub-queries steered retrieval.
    assert [t for t, _ in llm.calls] == ["facts", "determine"]
    prompt = llm.calls[1][1][1]["content"]
    assert "pep_status: foreign" in prompt and "[S1]" in prompt


def test_hallucinated_citations_are_removed_and_answer_withheld(built_cfg):
    llm = ScriptedLLM(FPEP_FACTS, {"tier": "standard", "summary": "Standard.",
                                   "reasoning": [{"point": "Made-up rule.", "sources": ["S42"]}],
                                   "required_measures": [], "missing_information": [], "confidence": "high"})
    r = _assistant(built_cfg, llm, **{"verification.guardrails": False}).determine(SCENARIO)
    assert r["abstained"] and r["tier"] == ABSTAIN
    assert r["checks"]["citation_validity"] == 0.0
    assert "without any valid citation" in r["abstain_reason"]


def test_guardrail_escalates_under_applied_tier(built_cfg):
    llm = ScriptedLLM(FPEP_FACTS, {"tier": "standard", "summary": "Standard CDD.",
                                   "reasoning": [{"point": "Collect KYC information for the individual customer.",
                                                  "sources": ["S2"]}],
                                   "required_measures": [], "missing_information": [], "confidence": "high"})
    r = _assistant(built_cfg, llm).determine(SCENARIO)
    assert r["model_tier"] == "standard" and r["tier"] == "enhanced"
    assert r["escalated"] and r["needs_review"] and "foreign_pep" in r["guardrails_fired"]
    assert any(p["text"].startswith("Escalated by guardrail") and p["citations"] for p in r["points"])


def test_low_similarity_abstains_before_generation(built_cfg):
    llm = ScriptedLLM(FPEP_FACTS, {})
    r = _assistant(built_cfg, llm, **{"retrieval.min_dense_similarity": 0.99}).determine(SCENARIO)
    assert r["abstained"] and r["tier"] == ABSTAIN
    assert [t for t, _ in llm.calls] == ["facts"]  # generator never called


def test_model_can_abstain(built_cfg):
    llm = ScriptedLLM(FPEP_FACTS, {"tier": "insufficient_information", "summary": "Need the risk rating.",
                                   "reasoning": [], "required_measures": [], "missing_information": ["risk rating"],
                                   "confidence": "low"})
    r = _assistant(built_cfg, llm).determine("A customer wants an account.")
    assert r["abstained"] and r["missing_information"] == ["risk rating"]


def test_generator_failure_is_reported_not_raised(built_cfg):
    r = _assistant(built_cfg, ScriptedLLM(FPEP_FACTS, fail=True)).determine(SCENARIO)
    assert r["abstained"] and "failed" in r["abstain_reason"]


def test_explain_unanswerable(built_cfg):
    llm = ScriptedLLM(answer={"answerable": False, "summary": "Not covered.", "key_points": [],
                              "missing_information": [], "confidence": "low"})
    # Force past the similarity gate so the model's own refusal is what is tested.
    r = _assistant(built_cfg, llm, **{"retrieval.min_dense_similarity": -1.0}).explain(
        "What is the penalty for speeding?")
    assert r["abstained"] and r["points"] == []
    assert [t for t, _ in llm.calls] == ["explain"]  # no fact extraction in explain mode


def test_out_of_scope_question_refused_by_similarity_gate(built_cfg):
    llm = ScriptedLLM(answer={})
    r = _assistant(built_cfg, llm, **{"retrieval.min_dense_similarity": 0.5}).explain("Penalty for speeding?")
    assert r["abstained"] and llm.calls == []


def test_fact_extraction_can_be_disabled(built_cfg):
    llm = ScriptedLLM(FPEP_FACTS, {"tier": "enhanced", "summary": "x", "reasoning": [
        {"point": "foreign politically exposed person source of wealth", "sources": ["S1"]}],
        "required_measures": [], "missing_information": [], "confidence": "medium"})
    r = _assistant(built_cfg, llm, **{"retrieval.use_fact_extraction": False}).determine(SCENARIO)
    assert [t for t, _ in llm.calls] == ["determine"] and r["facts"] is None


def test_offline_stub_end_to_end(assistant):
    r = assistant.determine(SCENARIO)
    assert r["offline_stub"] and r["tier"] == "enhanced"
    r2 = assistant.explain("What KYC information do we collect for an individual?")
    assert not r2["abstained"] and r2["points"]
