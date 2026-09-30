"""Gold-standard test set: schema, loading and validation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from amlrag import ABSTAIN, TIERS

VALID_MODES = ("determine", "explain")
VALID_STATUS = ("draft", "reviewed")
# Walert's question categories, plus "underspecified" for scenarios that are in scope
# but don't give enough facts to decide.
ANSWER_TYPES = ("known", "inferred", "out_of_kb", "underspecified")


@dataclass
class GoldItem:
    id: str
    mode: str
    query: str
    answerable: bool = True
    expected_tier: str | None = None
    acceptable_tiers: list[str] = field(default_factory=list)
    mandatory_ecdd: bool = False
    expected_sections: list[str] = field(default_factory=list)     # graded "highly relevant" (2)
    partial_sections: list[str] = field(default_factory=list)      # graded "partially relevant" (1)
    reference_answer: str = ""
    answer_type: str = ""
    key_facts: list[list[str]] = field(default_factory=list)
    customer_type: str | None = None
    group: str | None = None
    counterfactual_of: str | None = None
    tags: list[str] = field(default_factory=list)
    difficulty: str = "medium"
    status: str = "draft"
    reviewer: str | None = None
    notes: str = ""

    @property
    def acceptable(self) -> list[str]:
        return self.acceptable_tiers or ([self.expected_tier] if self.expected_tier else [])

    @property
    def category(self) -> str:
        """Walert-style category; derived when answer_type is left blank."""
        if self.answer_type:
            return self.answer_type
        if not self.answerable:
            return "underspecified" if self.mode == "determine" else "out_of_kb"
        return "known"

    @property
    def is_variant(self) -> bool:
        return bool(self.counterfactual_of)

    def relevance(self) -> dict[str, int]:
        """Graded relevance per reference (2 = highly relevant, 1 = partially relevant)."""
        grades = {r: 1 for r in self.partial_sections}
        grades.update({r: 2 for r in self.expected_sections})
        return grades

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
    if item.answer_type and item.answer_type not in ANSWER_TYPES:
        errs.append(f"answer_type must be one of {ANSWER_TYPES}")
    if item.answerable and item.category in ("out_of_kb", "underspecified"):
        errs.append(f"answer_type {item.category!r} requires answerable: false")
    if not item.answerable and item.category not in ("out_of_kb", "underspecified"):
        errs.append("unanswerable items must have answer_type out_of_kb or underspecified")
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
    if item.answerable and not item.reference_answer.strip():
        errs.append("answerable items need a reference_answer (used for ROUGE-1 / BERTScore)")
    if set(item.expected_sections) & set(item.partial_sections):
        errs.append("a reference cannot be both expected and partial")
    for fact in item.key_facts:
        if not isinstance(fact, list) or not fact or not all(isinstance(a, str) for a in fact):
            errs.append("key_facts must be a list of lists of alternative phrases")
            break
    return errs


def _validate_counterfactuals(items: list[GoldItem]) -> list[str]:
    by_id = {i.id: i for i in items}
    errs = []
    for v in items:
        if not v.counterfactual_of:
            continue
        base = by_id.get(v.counterfactual_of)
        if base is None:
            errs.append(f"{v.id}: counterfactual_of {v.counterfactual_of!r} does not exist")
            continue
        if base.counterfactual_of:
            errs.append(f"{v.id}: base {base.id} is itself a variant")
        if (v.mode, v.expected_tier, sorted(v.acceptable), v.answerable) != \
                (base.mode, base.expected_tier, sorted(base.acceptable), base.answerable):
            errs.append(f"{v.id}: a counterfactual must expect the same answer as its base {base.id}")
        if v.query.strip() == base.query.strip():
            errs.append(f"{v.id}: identical query to its base")
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
    problems += _validate_counterfactuals(items)
    if problems:
        raise ValueError("gold set has problems:\n  " + "\n  ".join(problems))
    return items
