"""SQLite log of every query, so a compliance manager can see where the assistant is unsure.

Privacy: questions can contain customer details. By default the text is passed
through amlrag.redact before it is written (store_text: redacted), rows are
deleted after retention_days, and the "why flagged" column only ever holds
system-generated text, never the model's wording (which can repeat names).
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from amlrag.redact import redact

_SCHEMA = """
CREATE TABLE IF NOT EXISTS queries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  mode TEXT NOT NULL,
  query TEXT,
  tier TEXT,
  confidence TEXT,
  abstained INTEGER NOT NULL,
  needs_review INTEGER NOT NULL,
  reason TEXT,
  citations TEXT,
  latency_s REAL,
  feedback TEXT,
  text_mode TEXT
);
CREATE INDEX IF NOT EXISTS idx_queries_flags ON queries (abstained, needs_review, confidence);
CREATE INDEX IF NOT EXISTS idx_queries_ts ON queries (ts);
"""

TEXT_MODES = ("full", "redacted", "none")


class QueryLog:
    def __init__(self, path: Path, store_text: str = "redacted", retention_days: int = 30, enabled: bool = True):
        if store_text not in TEXT_MODES:
            raise ValueError(f"query_log.store_text must be one of {TEXT_MODES}, got {store_text!r}")
        self.path = path
        self.store_text = store_text
        self.retention_days = int(retention_days or 0)
        self.enabled = enabled
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.executescript(_SCHEMA)
            cols = {r["name"] for r in con.execute("PRAGMA table_info(queries)")}
            if "text_mode" not in cols:                      # database from v0.1
                con.execute("ALTER TABLE queries ADD COLUMN text_mode TEXT")
        self.purge_expired()

    @classmethod
    def from_config(cls, cfg) -> "QueryLog":
        q = cfg.get("query_log", {})
        return cls(cfg.path("query_log"), q.get("store_text", "redacted"), q.get("retention_days", 30),
                   q.get("enabled", True))

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def _text(self, text: str) -> str | None:
        if self.store_text == "none":
            return None
        return text if self.store_text == "full" else redact(text)

    @staticmethod
    def _reason(result: dict[str, Any]) -> str | None:
        """System-generated reason only; model text can repeat customer names."""
        parts = []
        if result.get("flag_reason"):
            parts.append(result["flag_reason"])
        parts += list(result.get("warnings", []))[:3]
        if not parts and result.get("confidence") == "low":
            parts.append("Low confidence")
        return "; ".join(parts) or None

    def record(self, result: dict[str, Any]) -> int | None:
        if not self.enabled:
            return None
        cites = sorted({c["chunk_id"] for p in result.get("points", []) for c in p.get("citations", [])
                        if c.get("chunk_id")})
        with self._lock, self._connect() as con:
            cur = con.execute(
                "INSERT INTO queries (ts, mode, query, tier, confidence, abstained, needs_review, reason, citations,"
                " latency_s, text_mode) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), result["mode"],
                 self._text(result["query"]), result.get("tier"), result.get("confidence"),
                 int(bool(result.get("abstained"))), int(bool(result.get("needs_review"))), self._reason(result),
                 json.dumps(cites), result.get("timings", {}).get("total_s"), self.store_text))
            row_id = int(cur.lastrowid)
        self.purge_expired()
        return row_id

    def feedback(self, query_id: int, value: str) -> bool:
        with self._lock, self._connect() as con:
            cur = con.execute("UPDATE queries SET feedback=? WHERE id=?", (value[:40], query_id))
            return cur.rowcount > 0

    def purge_expired(self) -> int:
        if self.retention_days <= 0:
            return 0
        return self.purge_older_than(self.retention_days)

    def purge_older_than(self, days: int) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
        with self._lock, self._connect() as con:
            return con.execute("DELETE FROM queries WHERE ts < ?", (cutoff,)).rowcount

    def purge_all(self) -> int:
        with self._lock, self._connect() as con:
            n = con.execute("DELETE FROM queries").rowcount
        with self._connect() as con:
            con.execute("VACUUM")        # actually remove deleted text from the database file
        return n

    def gaps(self, limit: int = 200) -> list[dict[str, Any]]:
        """Queries the assistant could not answer confidently, newest first."""
        with self._connect() as con:
            rows = con.execute(
                "SELECT * FROM queries WHERE abstained=1 OR needs_review=1 OR confidence='low' "
                "OR feedback='not_helpful' ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def summary(self) -> dict[str, Any]:
        with self._connect() as con:
            total = con.execute("SELECT COUNT(*) FROM queries").fetchone()[0]
            abst = con.execute("SELECT COUNT(*) FROM queries WHERE abstained=1").fetchone()[0]
            review = con.execute("SELECT COUNT(*) FROM queries WHERE needs_review=1").fetchone()[0]
            low = con.execute("SELECT COUNT(*) FROM queries WHERE confidence='low'").fetchone()[0]
            by_tier = dict(con.execute("SELECT COALESCE(tier,'-'), COUNT(*) FROM queries GROUP BY tier").fetchall())
        return {"total": total, "abstained": abst, "needs_review": review, "low_confidence": low, "by_tier": by_tier,
                "store_text": self.store_text, "retention_days": self.retention_days}
