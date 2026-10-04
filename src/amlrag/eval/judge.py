"""LLM-as-judge for claim-level faithfulness (with an on-disk cache)."""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from amlrag.generate.prompts import JUDGE_SCHEMA, judge_messages

log = logging.getLogger(__name__)


class Judge:
    def __init__(self, llm, cache_path: Path | None = None):
        self.llm = llm
        self.name = getattr(llm, "name", "judge")
        self.cache_path = cache_path
        self.cache: dict[str, bool] = {}
        if cache_path and cache_path.exists():
            self.cache = json.loads(cache_path.read_text(encoding="utf-8"))

    def _key(self, claim: str, passages: list[str], scenario: str | None) -> str:
        h = hashlib.sha256((self.name + "\x00" + claim + "\x00" + "\x00".join(passages)
                            + ("\x01" + scenario if scenario else "")).encode())
        return h.hexdigest()[:24]

    def supported(self, claim: str, passages: list[str], scenario: str | None = None) -> bool | None:
        """Judge a claim against cited passages and, for facts and conclusions, the scenario."""
        if not passages and not scenario:
            return False
        key = self._key(claim, passages, scenario)
        if key in self.cache:
            return self.cache[key]
        try:
            out, _ = self.llm.chat_json(judge_messages(claim, passages, scenario), JUDGE_SCHEMA, task="judge")
            verdict = bool(out.get("supported"))
        except Exception as exc:
            log.warning("judge failed: %s", exc)
            return None
        self.cache[key] = verdict
        return verdict

    def save(self) -> None:
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self.cache), encoding="utf-8")
