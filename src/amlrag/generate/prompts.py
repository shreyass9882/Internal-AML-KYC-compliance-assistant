"""Prompts and JSON schemas for the two answer modes.

Kept short on purpose: 8-9B local models follow a compact, rule-numbered prompt
more reliably than a long one, and every token here competes with the sources
for the context window.
"""
from __future__ import annotations

from typing import Any

from amlrag.models import Retrieved

_POINT = {
    "type": "object",
    "properties": {"point": {"type": "string"}, "sources": {"type": "array", "items": {"type": "string"}}},
    "required": ["point", "sources"],
}
_MEASURE = {
    "type": "object",
    "properties": {"measure": {"type": "string"}, "sources": {"type": "array", "items": {"type": "string"}}},
    "required": ["measure", "sources"],
}

DETERMINE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "tier": {"type": "string", "enum": ["simplified", "standard", "enhanced", "insufficient_information"]},
        "summary": {"type": "string"},
        "reasoning": {"type": "array", "items": _POINT},
        "required_measures": {"type": "array", "items": _MEASURE},
        "missing_information": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["tier", "summary", "reasoning", "required_measures", "missing_information", "confidence"],
}

EXPLAIN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "answerable": {"type": "boolean"},
        "summary": {"type": "string"},
        "key_points": {"type": "array", "items": _POINT},
        "missing_information": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["answerable", "summary", "key_points", "missing_information", "confidence"],
}

_COMMON_RULES = """- Use ONLY the numbered SOURCES. Do not use outside knowledge, even if you are confident.
- Every point must cite at least one source label exactly as written, e.g. "S2". Cite only labels that appear in SOURCES.
- Cite the source that states the rule itself, not a source that merely mentions the topic.
- Write for a new compliance team member: plain English, short sentences, explain any legal term you use.
- confidence: "high" only if a source states the rule directly for this situation; "medium" if you applied a general rule; "low" otherwise."""

_TIERS = """Tiers:
- "enhanced": the sources require enhanced CDD in this situation.
- "simplified": the sources permit simplified CDD AND the scenario meets every condition the sources set (for example low ML/TF risk and no enhanced CDD trigger).
- "standard": ordinary initial CDD applies, with neither simplification nor enhancement.
- "insufficient_information": the sources or the scenario do not let you decide. List what is missing in missing_information."""

_METHOD = """Method:
1. First check the sources for enhanced CDD triggers that match the scenario. If one applies, the tier is "enhanced" even if the customer would otherwise qualify for simplified CDD.
2. Otherwise check whether every condition for simplified CDD is met.
3. Otherwise the tier is "standard"."""

DETERMINE_SYSTEM = f"""You help compliance officers at an Australian AML/CTF reporting entity decide which customer due diligence (CDD) tier applies to a customer scenario. Your sources are AUSTRAC guidance and the AML/CTF Rules 2025.

{_TIERS}

{_METHOD}

Rules:
{_COMMON_RULES}
- reasoning: 2-5 points explaining the decision. required_measures: the concrete CDD steps the sources require for this tier."""

EXPLAIN_SYSTEM = f"""You explain Australian AML/CTF customer due diligence obligations to compliance staff, using AUSTRAC guidance and the AML/CTF Rules 2025.

Rules:
{_COMMON_RULES}
- If the sources do not answer the question, set answerable to false, give a one-sentence summary saying so, and leave key_points empty. Never fill the gap from memory.
- key_points: 2-6 points, each one fact or step."""


def source_block(results: list[Retrieved]) -> tuple[str, dict[str, Retrieved]]:
    """Render retrieved chunks as numbered sources and return the label -> chunk map."""
    label_map: dict[str, Retrieved] = {}
    blocks = []
    for i, r in enumerate(results, start=1):
        label = f"S{i}"
        label_map[label] = r
        header = r.chunk.citation
        if r.chunk.kind == "guidance" and r.chunk.heading_path:
            header = f"{header} ({r.chunk.heading_path})"
        blocks.append(f"[{label}] {header}\n{r.chunk.text}")
    return "\n\n".join(blocks), label_map


def _facts_lines(facts: dict[str, Any] | None) -> str:
    if not facts:
        return ""
    lines = []
    for k, v in facts.items():
        if k == "missing_information" or v in (False, "unknown", "none", None, []):
            continue
        lines.append(f"- {k}: {v}")
    if not lines:
        return ""
    return "FACTS EXTRACTED FROM THE SCENARIO (check them against the scenario; they may be incomplete):\n" + \
        "\n".join(lines) + "\n\n"


def determine_messages(scenario: str, results: list[Retrieved], facts: dict[str, Any] | None):
    sources, label_map = source_block(results)
    user = (f"SCENARIO:\n{scenario.strip()}\n\n{_facts_lines(facts)}SOURCES:\n{sources}\n\n"
            "Return the JSON object.")
    return [{"role": "system", "content": DETERMINE_SYSTEM}, {"role": "user", "content": user}], label_map


def explain_messages(question: str, results: list[Retrieved]):
    sources, label_map = source_block(results)
    user = f"QUESTION:\n{question.strip()}\n\nSOURCES:\n{sources}\n\nReturn the JSON object."
    return [{"role": "system", "content": EXPLAIN_SYSTEM}, {"role": "user", "content": user}], label_map


JUDGE_SYSTEM = """You check whether a claim is fully supported by the given passages.
Answer supported=true only if the passages state or directly entail every part of the claim. Missing detail, a different condition, or an extra requirement means supported=false."""

JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"supported": {"type": "boolean"}, "reason": {"type": "string"}},
    "required": ["supported", "reason"],
}


def judge_messages(claim: str, passages: list[str]):
    body = "\n\n".join(f"[P{i}] {p}" for i, p in enumerate(passages, start=1))
    return [{"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": f"CLAIM:\n{claim}\n\nPASSAGES:\n{body}\n\nReturn the JSON object."}]


# --------------------------------------------------------------------------- closed-book baseline
# The same task with no retrieved sources: the model answers from its own training
# and names its legal basis. Used only as an evaluation baseline to measure what
# retrieval adds (preset "closed_book").

_REF_POINT = {
    "type": "object",
    "properties": {"point": {"type": "string"}, "reference": {"type": "string"}},
    "required": ["point", "reference"],
}
_REF_MEASURE = {
    "type": "object",
    "properties": {"measure": {"type": "string"}, "reference": {"type": "string"}},
    "required": ["measure", "reference"],
}

CLOSED_DETERMINE_SCHEMA: dict[str, Any] = {
    **DETERMINE_SCHEMA,
    "properties": {**DETERMINE_SCHEMA["properties"],
                   "reasoning": {"type": "array", "items": _REF_POINT},
                   "required_measures": {"type": "array", "items": _REF_MEASURE}},
}
CLOSED_EXPLAIN_SCHEMA: dict[str, Any] = {
    **EXPLAIN_SCHEMA,
    "properties": {**EXPLAIN_SCHEMA["properties"], "key_points": {"type": "array", "items": _REF_POINT}},
}

_CLOSED_RULES = """- No reference material is provided. Answer from your own knowledge of Australian AML/CTF law as it applies from 31 March 2026: the AML/CTF Act 2006 as amended in 2024, and the AML/CTF Rules 2025.
- For every point, give in "reference" the specific provision you rely on, for example "AML/CTF Rules 2025 s 6-23" or "AML/CTF Act s 32". Write "none" if you cannot name one. Do not invent references.
- Write for a new compliance team member: plain English, short sentences.
- confidence: "high" only if you are certain of the rule and its reference; "medium" if you applied a general rule; "low" otherwise."""

_CLOSED_TIERS = (_TIERS.replace("the sources require", "the law requires")
                 .replace("the sources permit", "the law permits")
                 .replace("the sources set", "the law sets")
                 .replace("the sources or the scenario do not", "the law or the scenario does not"))

CLOSED_DETERMINE_SYSTEM = f"""You help compliance officers at an Australian AML/CTF reporting entity decide which customer due diligence (CDD) tier applies to a customer scenario.

{_CLOSED_TIERS}

{_METHOD.replace("check the sources for", "check for")}

Rules:
{_CLOSED_RULES}
- If you are not sure what the law requires, choose "insufficient_information" rather than guessing.
- reasoning: 2-5 points explaining the decision. required_measures: the concrete CDD steps the law requires for this tier."""

CLOSED_EXPLAIN_SYSTEM = f"""You explain Australian AML/CTF customer due diligence obligations to compliance staff.

Rules:
{_CLOSED_RULES}
- If you do not know the answer, set answerable to false, give a one-sentence summary saying so, and leave key_points empty.
- key_points: 2-6 points, each one fact or step."""


def closed_determine_messages(scenario: str):
    return [{"role": "system", "content": CLOSED_DETERMINE_SYSTEM},
            {"role": "user", "content": f"SCENARIO:\n{scenario.strip()}\n\nReturn the JSON object."}]


def closed_explain_messages(question: str):
    return [{"role": "system", "content": CLOSED_EXPLAIN_SYSTEM},
            {"role": "user", "content": f"QUESTION:\n{question.strip()}\n\nReturn the JSON object."}]
