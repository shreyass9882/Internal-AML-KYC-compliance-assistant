"""SQLite log of every query, so a compliance manager can see where the assistant is unsure."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS queries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  mode TEXT NOT NULL,
  query TEXT NOT NULL,
  tier TEXT,
  confidence TEXT,
  abstained INTEGER NOT NULL,
  needs_review INTEGER NOT NULL,
  reason TEXT,
  citations TEXT,
  latency_s REAL,
  feedback TEXT
);
CREATE INDEX IF NOT EXISTS idx_queries_flags ON queries (abstained, needs_review, confidence);
"""


class QueryLog:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.Lock()
        with self._connect() as con:
            con.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def record(self, result: dict[str, Any]) -> int:
        reason = result.get("abstain_reason") or "; ".join(result.get("warnings", [])[:3]) or None
        cites = sorted({c["chunk_id"] for p in result.get("points", []) for c in p.get("citations", [])})
        with self._lock, self._connect() as con:
            cur = con.execute(
                "INSERT INTO queries (ts, mode, query, tier, confidence, abstained, needs_review, reason, citations, latency_s)"
                " VALUES (?,?,?,?,?,?,?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), result["mode"], result["query"],
                 result.get("tier"), result.get("confidence"), int(bool(result.get("abstained"))),
                 int(bool(result.get("needs_review"))), reason, json.dumps(cites),
                 result.get("timings", {}).get("total_s")))
            return int(cur.lastrowid)

    def feedback(self, query_id: int, value: str) -> bool:
        with self._lock, self._connect() as con:
            cur = con.execute("UPDATE queries SET feedback=? WHERE id=?", (value[:40], query_id))
            return cur.rowcount > 0

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
        return {"total": total, "abstained": abst, "needs_review": review, "low_confidence": low, "by_tier": by_tier}
