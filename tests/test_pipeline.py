"""End-to-end pipeline behaviour with scripted model outputs (no Ollama needed)."""
from amlrag import ABSTAIN
from amlrag.pipeline import Assistant
from amlrag.generate.prompts import PROMPT_VERSION


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


def test_typed_reasoning_is_checked_against_its_own_evidence(built_cfg):
    """Scenario facts need no citation (checked against the scenario); rules and conclusions do."""
    llm = ScriptedLLM(FPEP_FACTS, {
        "tier": "enhanced", "summary": "Enhanced CDD applies.",
        "reasoning": [
            {"kind": "scenario_fact", "point": "The customer is a serving minister in a foreign government.",
             "sources": []},
            {"kind": "scenario_fact", "point": "The customer holds three passports from Ruritania.", "sources": []},
            {"kind": "rule", "point": "A foreign politically exposed person requires source of wealth and source "
                                      "of funds.", "sources": ["S1"]},
            {"kind": "conclusion", "point": "The minister is a foreign politically exposed person, so source of "
                                            "wealth and source of funds must be established.", "sources": ["S1"]},
        ],
        "required_measures": [], "missing_information": [], "confidence": "high"})
    r = _assistant(built_cfg, llm, **{"verification.guardrails": False}).determine(SCENARIO)
    pts = r["points"]
    assert [p["kind"] for p in pts] == ["scenario_fact", "scenario_fact", "rule", "conclusion"]
    assert pts[0]["supported"] is True and pts[0]["citations"] == []
    assert pts[1]["supported"] is False            # not in the scenario
    assert pts[2]["supported"] is True and pts[3]["supported"] is True
    assert r["checks"]["uncited_points"] == 0      # facts from the scenario are not "uncited"
    assert r["prompt_version"] == PROMPT_VERSION
    assert not r["abstained"]


def test_answer_with_only_scenario_facts_is_withheld(built_cfg):
    llm = ScriptedLLM(FPEP_FACTS, {"tier": "standard", "summary": "Standard.",
                                   "reasoning": [{"kind": "scenario_fact", "point": "The customer is a minister.",
                                                  "sources": []}],
                                   "required_measures": [], "missing_information": [], "confidence": "high"})
    r = _assistant(built_cfg, llm, **{"verification.guardrails": False}).determine(SCENARIO)
    assert r["abstained"] and r["tier"] == ABSTAIN


def test_prompt_v2_instructions():
    from amlrag.generate.prompts import (CLOSED_DETERMINE_SYSTEM, DETERMINE_SCHEMA, DETERMINE_SYSTEM, POINT_KINDS,
                                         determine_messages, judge_messages)

    item = DETERMINE_SCHEMA["properties"]["reasoning"]["items"]
    assert item["properties"]["kind"]["enum"] == POINT_KINDS and "kind" in item["required"]
    assert "insufficient_information" in DETERMINE_SYSTEM and "every condition" in DETERMINE_SYSTEM
    # The closed-book baseline has no sources, so its method must not mention them.
    assert "source" not in CLOSED_DETERMINE_SYSTEM.split("Method:")[1].split("Rules:")[0]
    msgs, _ = determine_messages("A customer.", [], {"pep_status": "foreign"})
    assert "may be wrong" in msgs[1]["content"]
    j = judge_messages("claim", [], scenario="The scenario.")[1]["content"]
    assert "SCENARIO:\nThe scenario." in j and "PASSAGES" not in j


def test_undescribed_customer_is_not_given_a_default_tier(built_cfg):
    from amlrag.pipeline import FLAG_UNDESCRIBED, undescribed_customer

    empty = {**FPEP_FACTS, "customer_type": "unknown", "pep_status": "none", "ml_tf_risk": "unknown"}
    llm = ScriptedLLM(empty, {"tier": "standard", "summary": "Standard applies by default.",
                              "reasoning": [{"kind": "rule", "point": "Customer due diligence applies.",
                                             "sources": ["S1"]}],
                              "required_measures": [], "missing_information": ["who the customer is"],
                              "confidence": "medium"})
    r = _assistant(built_cfg, llm, **{"verification.guardrails": False}).determine(
        "A customer wants to open an account. Which CDD tier applies?")
    assert r["tier"] == ABSTAIN and r["abstained"] and r["flag_reason"] == FLAG_UNDESCRIBED
    assert r["points"] == [] and "doesn't say who" in r["summary"]
    # A described customer, a long scenario, or any extracted fact is left alone.
    assert not undescribed_customer({**empty, "customer_type": "individual"}, "An individual opens an account.")
    assert not undescribed_customer({**empty, "nested_services": True}, "A customer opens an account.")
    assert not undescribed_customer(empty, " ".join(["word"] * 40))


def test_each_subquery_keeps_its_best_passage(assistant):
    r = assistant.retriever
    sub = "simplified customer due diligence beneficial owners 6-18"
    best = max(r.bm25.query(sub, 5), key=lambda x: x[1])[0]
    res = r.search("customer due diligence for a new customer", [sub], k=2)
    assert best in [x.chunk.chunk_id for x in res]
    assert [x.rrf_score for x in res] == sorted((x.rrf_score for x in res), reverse=True)


class SequenceLLM(ScriptedLLM):
    """Returns the given answers in turn (facts calls are answered separately)."""

    def __init__(self, facts, answers):
        super().__init__(facts, answers[0])
        self.answers = list(answers)

    def chat_json(self, messages, schema=None, task=""):
        self.calls.append((task, messages))
        if task == "facts":
            return self.facts, {"latency_s": 0.0}
        return self.answers.pop(0) if len(self.answers) > 1 else self.answers[0], {"latency_s": 0.0}


def test_uncited_explain_answer_is_retried_once(built_cfg):
    first = {"answerable": True, "summary": "Record the steps and collect the CEO's details.", "key_points": [],
             "missing_information": [], "confidence": "high"}
    second = {**first, "key_points": [{"point": "A foreign politically exposed person requires source of wealth "
                                                "and source of funds.", "sources": ["S1"]}]}
    llm = SequenceLLM({}, [first, second])
    r = _assistant(built_cfg, llm).explain("What extra checks apply to a foreign politically exposed person?")
    assert not r["abstained"] and r["checks"]["retried_uncited"] is True
    assert [t for t, _ in llm.calls] == ["explain", "explain"]
    assert "no points that cite" in llm.calls[1][1][-1]["content"]


def test_retry_that_still_cites_nothing_is_withheld(built_cfg):
    empty = {"answerable": True, "summary": "Something.", "key_points": [], "missing_information": [],
             "confidence": "high"}
    r = _assistant(built_cfg, SequenceLLM({}, [empty, empty])).explain("What is a foreign PEP?")
    assert r["abstained"] and r["checks"]["retried_uncited"] is False


def test_model_abstention_is_not_retried(built_cfg):
    llm = SequenceLLM({}, [{"answerable": False, "summary": "Not covered.", "key_points": [],
                            "missing_information": [], "confidence": "low"}])
    r = _assistant(built_cfg, llm).explain("What is a foreign PEP?")
    assert r["abstained"] and [t for t, _ in llm.calls] == ["explain"]
