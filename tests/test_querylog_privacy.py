"""Query-log privacy: redaction, storage modes, retention."""
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from amlrag.querylog import QueryLog
from amlrag.redact import redact


@pytest.mark.parametrize("text, must_hide, must_keep", [
    ("Emily Walker, an Australian-resident nurse born in Melbourne.", ["Emily", "Walker"], ["Australian-resident", "Melbourne"]),
    ("Mr John O'Brien of 12 Smith Street, Richmond", ["John", "O'Brien", "12 Smith Street"], ["Mr"] and []),
    ("phone 0412 345 678 or +61 3 9123 4567", ["0412", "9123"], ["phone"]),
    ("DOB 03/04/1985, born 12 March 1985, updated March 3, 2020", ["03/04/1985", "12 March 1985", "March 3, 2020"], ["DOB"]),
    ("account 062-000 12345678, card 4111 1111 1111 1111, ABN 51 824 753 556", ["12345678", "4111", "824 753"], ["account", "ABN"]),
    ("email jo.smith@example.com, customer #48213", ["jo.smith", "48213"], ["customer"]),
    ("a customer named Wei Zhang and a sole trader called Tran Van Minh", ["Wei", "Zhang", "Tran", "Minh"], ["sole trader"]),
    ("The Nguyen Family Trust and Harbourline Imports Pty Ltd", ["Nguyen", "Harbourline"], ["Family Trust", "Pty Ltd"]),
])
def test_redact_masks_identifiers(text, must_hide, must_keep):
    out = redact(text)
    for s in must_hide:
        assert s not in out, (s, out)
    for s in must_keep:
        assert s in out, (s, out)


@pytest.mark.parametrize("text", [
    "An individual customer is a serving deputy minister of finance in New Zealand.",
    "See rule 6-23 and section 32 of the Act; deposits just below $10,000 and 45% of shares.",
    "A company incorporated in a country subject to a FATF call for action. APRA-regulated, ASX-listed, SMSF.",
    "Our bank's branch in Singapore opens an account for a Singaporean government minister.",
])
def test_redact_leaves_ordinary_scenarios_alone(text):
    assert redact(text) == text


def test_known_limitation_sentence_initial_first_name():
    # Documented: a lone first name opening a sentence is not caught.
    assert redact("Maria wants an account.") == "Maria wants an account."


RESULT = {"mode": "determine", "query": "Emily Walker, phone 0412 345 678, is a foreign PEP.", "tier": "enhanced",
          "confidence": "low", "abstained": False, "needs_review": True, "warnings": ["1 of 2 point(s) are weak."],
          "summary": "Emily Walker is a foreign PEP.", "points": [], "timings": {"total_s": 1.2}}


def _row(log, rid):
    con = sqlite3.connect(log.path)
    con.row_factory = sqlite3.Row
    return dict(con.execute("SELECT * FROM queries WHERE id=?", (rid,)).fetchone())


def test_modes(tmp_path):
    full = QueryLog(tmp_path / "a.db", "full", 0)
    assert _row(full, full.record(RESULT))["query"] == RESULT["query"]
    red = QueryLog(tmp_path / "b.db", "redacted", 0)
    row = _row(red, red.record(RESULT))
    assert "Emily" not in row["query"] and "0412" not in row["query"] and "foreign PEP" in row["query"]
    none = QueryLog(tmp_path / "c.db", "none", 0)
    row = _row(none, none.record(RESULT))
    assert row["query"] is None and row["tier"] == "enhanced" and row["text_mode"] == "none"
    with pytest.raises(ValueError):
        QueryLog(tmp_path / "d.db", "partial")


def test_reason_never_contains_model_text(tmp_path):
    log = QueryLog(tmp_path / "a.db", "full", 0)
    row = _row(log, log.record({**RESULT, "flag_reason": "Tier escalated by guardrail"}))
    assert "Emily" not in (row["reason"] or "") and row["reason"].startswith("Tier escalated")


def test_disabled_log_records_nothing(tmp_path):
    log = QueryLog(tmp_path / "a.db", "redacted", 30, enabled=False)
    assert log.record(RESULT) is None and log.summary()["total"] == 0


def test_retention_and_purge(tmp_path):
    log = QueryLog(tmp_path / "a.db", "redacted", 30)
    old_id = log.record(RESULT)
    old_ts = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat(timespec="seconds")
    with sqlite3.connect(log.path) as con:
        con.execute("UPDATE queries SET ts=? WHERE id=?", (old_ts, old_id))
    new_id = log.record(RESULT)                      # recording triggers the retention purge
    ids = {r["id"] for r in log.gaps()}
    assert old_id not in ids and new_id in ids
    assert log.purge_all() == 1 and log.summary()["total"] == 0


def test_old_database_is_migrated(tmp_path):
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as con:
        con.execute("CREATE TABLE queries (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, mode TEXT NOT NULL,"
                    " query TEXT NOT NULL, tier TEXT, confidence TEXT, abstained INTEGER NOT NULL, needs_review INTEGER"
                    " NOT NULL, reason TEXT, citations TEXT, latency_s REAL, feedback TEXT)")
    log = QueryLog(path, "redacted", 0)
    assert log.record(RESULT) > 0
