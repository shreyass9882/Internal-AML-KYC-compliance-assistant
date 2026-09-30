"""Parse free-text legal references ("AML/CTF Rules 2025 s 6-23", "section 32 of the Act").

Used by the closed-book baseline, where the model names its legal basis from
memory. Parsed references become ids in the same form as chunk ids
("rules2025::6-23", "amlctf-act::32") so the usual attribution metrics apply,
and each one is checked against the sections that exist in the snapshot.
"""
from __future__ import annotations

import re

_DASH = "‐‑‒–—-"
_RULES_SEC = re.compile(rf"(?<![\d.])(\d{{1,2}})\s*[{_DASH}]\s*(\d{{1,3}}[A-Z]?)(?![\d{_DASH}])")
_ACT_SEC = re.compile(rf"\b(?:ss?|sec|sect|section|sections)\.?\s*(\d{{1,3}}[A-Z]{{0,2}})\b(?!\s*[{_DASH}]\s*\d)", re.I)
_OLD_RULES_DOC = re.compile(r"rules\s*2007", re.I)
_OLD_RULES = re.compile(r"\bchapter\s+\d+|(?<![\d.])\d{1,2}\.\d{1,2}(?:\.\d{1,3})?(?![\d.])", re.I)
_ACT_RANGE = re.compile(rf"\b(?:ss|sections)\.?\s*(\d{{1,3}}[A-Z]{{0,2}})\s*[{_DASH}]\s*(\d{{1,3}}[A-Z]{{0,2}})\b", re.I)
_MAX_RULES_PART = 15
_ACT_WORD = re.compile(r"\bAct\b")
_NONE = re.compile(r"^\s*(none|n/?a|unknown|not sure|-)?\s*\.?\s*$", re.I)


def parse_references(text: str) -> list[str]:
    """Return reference ids in order of appearance, without duplicates.

    - Hyphenated numbers are Rules 2025 sections: "6-23" -> "rules2025::6-23".
    - Plain section numbers are Act sections: "s 32", "section 32 of the Act" -> "amlctf-act::32".
    - References to the repealed 2007 Rules ("Chapter 4", "4.13.3", "Rules 2007") become
      "rules2007::<ref>", which never exists in the snapshot, so they count as invalid.
    """
    if not text or _NONE.match(text):
        return []
    ids: list[str] = []

    def add(ref: str) -> None:
        if ref not in ids:
            ids.append(ref)

    old = [m.group(0) for m in _OLD_RULES.finditer(text)]
    for ref in old:
        add("rules2007::" + re.sub(r"\s+", "-", ref.strip().lower()))
    if _OLD_RULES_DOC.search(text) and not old:
        add("rules2007::unspecified")
    ranges = list(_ACT_RANGE.finditer(text))
    for m in ranges:
        add(f"amlctf-act::{m.group(1).upper()}")
        add(f"amlctf-act::{m.group(2).upper()}")
    range_spans = [m.span() for m in ranges]
    rules_spans = []
    for m in _RULES_SEC.finditer(text):
        if int(m.group(1)) > _MAX_RULES_PART or any(a <= m.start() < b for a, b in range_spans):
            continue
        rules_spans.append(m.span())
        add(f"rules2025::{int(m.group(1))}-{m.group(2)}")
    for m in _ACT_SEC.finditer(text):
        if any(a <= m.start(1) < b for a, b in rules_spans + range_spans):
            continue
        # "s 32" with no document named is read as the Act: Rules sections are hyphenated.
        if _ACT_WORD.search(text) or not re.search(r"\brules?\b", text, re.I):
            add(f"amlctf-act::{m.group(1).upper()}")
    return ids


def check_reference(ref: str, known_sections: set[str], indexed_docs: set[str]) -> bool | None:
    """True if the section exists in the snapshot, False if it does not, None if its document isn't indexed."""
    doc = ref.split("::", 1)[0]
    if doc == "rules2007":
        return False
    if doc not in indexed_docs:
        return None
    return ref in known_sections
