"""Closed-book baseline: no retrieval, references parsed from the model's answer and checked against the snapshot."""
import pytest

from amlrag import ABSTAIN
from amlrag.generate.references import check_reference, parse_references
from amlrag.pipeline import Assistant


@pytest.mark.parametrize("text, expected", [
    ("AML/CTF Rules 2025 s 6-23", ["rules2025::6-23"]),
    ("rule 6–23(1)(a)", ["rules2025::6-23"]),
    ("AML/CTF Act s 32", ["amlctf-act::32"]),
    ("section 32 of the Act and Rules 6-21", ["rules2025::6-21", "amlctf-act::32"]),
    ("s 28 and s 30", ["amlctf-act::28", "amlctf-act::30"]),
    ("Act ss 28-30", ["amlctf-act::28", "amlctf-act::30"]),
    ("Act s 36A", ["amlctf-act::36A"]),
    ("Rules 2007 Chapter 4, 4.13.3", ["rules2007::chapter-4", "rules2007::4.13.3"]),
    ("the old Rules 2007", ["rules2007::unspecified"]),
    ("none", []), ("N/A", []), ("", []),
    ("AUSTRAC guidance on politically exposed persons", []),
])
def test_parse_references(text, expected):
    assert parse_references(text) == expected


def test_check_reference():
    known, docs = {"rules2025::6-23"}, {"rules2025"}
    assert check_reference("rules2025::6-23", known, docs) is True
    assert check_reference("rules2025::6-99", known, docs) is False
    assert check_reference("amlctf-act::32", known, docs) is None       # Act not indexed: can't check
    assert check_reference("rules2007::chapter-4", known, docs) is False  # repealed: never valid


class ScriptedLLM:
    name = "scripted"

    def __init__(self, answer):
        self.answer = answer
        self.calls = []

    def chat_json(self, messages, schema=None, task=""):
        self.calls.append((task, messages, schema))
        return self.answer, {"latency_s": 0.0}


def _closed(cfg, llm):
    cfg = cfg.override("retrieval.enabled", False)
    base = Assistant.from_config(cfg)
    return Assistant(cfg, base.retriever, llm, base.embedder_name, base.snapshot)


def test_closed_book_determine_checks_references(built_cfg):
    llm = ScriptedLLM({"tier": "enhanced", "summary": "Enhanced CDD.", "confidence": "high", "missing_information": [],
                       "reasoning": [{"point": "Foreign PEPs need source of wealth.", "reference": "AML/CTF Rules 2025 s 6-23"},
                                     {"point": "Old rule.", "reference": "Rules 2007 Chapter 4"},
                                     {"point": "Made up.", "reference": "AML/CTF Rules 2025 s 6-99"},
                                     {"point": "Act.", "reference": "AML/CTF Act s 32"},
                                     {"point": "No idea.", "reference": "none"}],
                       "required_measures": []})
    r = _closed(built_cfg, llm).determine("A foreign minister opens an account.")
    assert [t for t, _, _ in llm.calls] == ["closed_determine"]       # no fact extraction, no retrieval
    system = llm.calls[0][1][0]["content"]
    assert "No reference material is provided" in system and "SOURCES" not in llm.calls[0][1][1]["content"]
    assert r["closed_book"] and r["tier"] == "enhanced" and r["sources"] == [] and r["needs_review"]
    assert r["confidence"] == "high"                                    # model's own claim, reported as-is
    exists = {c["chunk_id"]: c["exists"] for p in r["points"] for c in p["citations"]}
    assert exists == {"rules2025::6-23": True, "rules2007::chapter-4": False, "rules2025::6-99": False,
                      "amlctf-act::32": None}
    assert r["checks"]["verifiable_references"] == 3 and r["checks"]["citation_validity"] == pytest.approx(1 / 3, abs=1e-3)
    assert r["checks"]["uncited_points"] == 1


def test_closed_book_explain_abstain(built_cfg):
    llm = ScriptedLLM({"answerable": False, "summary": "I don't know.", "key_points": [], "confidence": "low",
                       "missing_information": []})
    r = _closed(built_cfg, llm).explain("What is the penalty?")
    assert r["abstained"] and r["points"] == [] and r["checks"]["citation_validity"] is None


def test_closed_book_bad_tier_is_abstain(built_cfg):
    r = _closed(built_cfg, ScriptedLLM({"tier": "platinum", "summary": "", "reasoning": [], "required_measures": [],
                                         "confidence": "high", "missing_information": []})).determine("x y z")
    assert r["tier"] == ABSTAIN and r["abstained"] and r["confidence"] == "low"


def test_closed_book_eval_preset(built_cfg):
    from amlrag.eval.runner import run_eval

    _, m = run_eval(built_cfg, preset="closed_book", verbose=False)
    assert m["run"]["preset"] == "closed_book"
    assert m["retrieval"]["n"] == 0 and m["headline"]["retrieval_recall_at_k"] is None
    assert m["faithfulness"]["points"] == 0 and m["headline"]["faithfulness"] is None
    assert m["tier"]["n"] > 0 and m["headline"]["citation_precision"] is not None
