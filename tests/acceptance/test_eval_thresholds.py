"""Acceptance tests: the gold-standard evaluation must meet the thresholds in config.yaml.

This is the "test" in Test-Driven RAG. It runs the real pipeline (Ollama +
the built index) over data/gold/scenarios.jsonl, so it is slow and opt-in:

    AMLRAG_RUN_EVAL=1 pytest tests/acceptance -v
    AMLRAG_RUN_EVAL=1 AMLRAG_EVAL_LIMIT=10 pytest tests/acceptance   # quick smoke run

Each threshold is its own test, so a failing run shows exactly which property
regressed (e.g. mandatory ECDD recall) rather than one opaque failure.
"""
import os

import pytest

from amlrag.config import load_config

pytestmark = [
    pytest.mark.eval,
    pytest.mark.skipif(os.environ.get("AMLRAG_RUN_EVAL") != "1", reason="set AMLRAG_RUN_EVAL=1 to run the live eval"),
]


@pytest.fixture(scope="module")
def metrics():
    from amlrag.eval.runner import run_eval

    limit = int(os.environ["AMLRAG_EVAL_LIMIT"]) if os.environ.get("AMLRAG_EVAL_LIMIT") else None
    _, m = run_eval(load_config(), preset=os.environ.get("AMLRAG_EVAL_PRESET", "full"), limit=limit)
    return m


THRESHOLDS = [
    "tier_accuracy_acceptable", "mandatory_ecdd_recall", "under_application_rate_max", "retrieval_recall_at_k",
    "citation_validity", "citation_precision", "faithfulness", "unanswerable_abstain_rate", "false_abstain_rate_max",
    "fairness_tier_flip_rate_max",
]


@pytest.mark.parametrize("name", THRESHOLDS)
def test_threshold(metrics, name):
    check = next(a for a in metrics["acceptance"] if a["name"] == name)
    op = ">=" if check["direction"] == "min" else "<="
    assert check["passed"], f"{check['metric']} = {check['value']} (required {op} {check['limit']})"


def test_no_item_errors(metrics):
    assert not metrics["errors"], f"items raised errors: {metrics['errors']}"
