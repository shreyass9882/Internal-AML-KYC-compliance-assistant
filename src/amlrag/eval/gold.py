"""Gold-standard test set: schema, loading and validation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from amlrag import ABSTAIN, TIERS

VALID_MODES = ("determine", "explain")
VALID_STATUS = ("draft", "reviewed")


@dataclass
class GoldItem:
    id: str
    mode: str
    query: str
    answerable: bool = True
    expected_tier: str | None = None
    acceptable_tiers: list[str] = field(default_factory=list)
    mandatory_ecdd: bool = False
    expected_sections: list[str] = field(default_factory=list)
    key_facts: list[list[str]] = field(default_factory=list)
    customer_type: str | None = None
    group: str | None = None
    tags: list[str] = field(default_factory=list)
    difficulty: str = "medium"
    status: str = "draft"
    reviewer: str | None = None
    notes: str = ""

    @property
    def acceptable(self) -> list[str]:
        return self.acceptable_tiers or ([self.expected_tier] if self.expected_tier else [])

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GoldItem":
        known = cls.__dataclass_fields__
        extra = set(d) - set(known)
        if extra:
            raise ValueError(f"{d.get('id')}: unknown fields {sorted(extra)}")
        return cls(**d)


def validate(item: GoldItem) -> list[str]:
    errs = []
    if item.mode not in VALID_MODES:
        errs.append(f"mode must be one of {VALID_MODES}")
    if item.status not in VALID_STATUS:
        errs.append(f"status must be one of {VALID_STATUS}")
    if not item.query.strip():
        errs.append("query is empty")
    if item.mode == "determine":
        allowed = (*TIERS, ABSTAIN)
        if item.expected_tier not in allowed:
            errs.append(f"expected_tier must be one of {allowed}")
        if item.answerable and item.expected_tier == ABSTAIN:
            errs.append("answerable determine items need a real tier")
        if not item.answerable and item.expected_tier != ABSTAIN:
            errs.append(f"unanswerable determine items must expect {ABSTAIN}")
        for t in item.acceptable_tiers:
            if t not in allowed:
                errs.append(f"acceptable tier {t!r} invalid")
        if item.expected_tier and item.acceptable_tiers and item.expected_tier not in item.acceptable_tiers:
            errs.append("expected_tier must be in acceptable_tiers")
        if item.mandatory_ecdd and item.expected_tier != "enhanced":
            errs.append("mandatory_ecdd items must expect 'enhanced'")
    elif item.expected_tier is not None:
        errs.append("explain items must not set expected_tier")
    if item.answerable and not item.expected_sections:
        errs.append("answerable items need at least one expected_sections reference")
    for fact in item.key_facts:
        if not isinstance(fact, list) or not fact or not all(isinstance(a, str) for a in fact):
            errs.append("key_facts must be a list of lists of alternative phrases")
            break
    return errs


def load_gold(path: str | Path) -> list[GoldItem]:
    items: list[GoldItem] = []
    problems: list[str] = []
    seen: set[str] = set()
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, start=1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                item = GoldItem.from_dict(json.loads(line))
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                problems.append(f"line {n}: {exc}")
                continue
            if item.id in seen:
                problems.append(f"line {n}: duplicate id {item.id}")
            seen.add(item.id)
            problems += [f"{item.id}: {e}" for e in validate(item)]
            items.append(item)
    if problems:
        raise ValueError("gold set has problems:\n  " + "\n  ".join(problems))
    return items
