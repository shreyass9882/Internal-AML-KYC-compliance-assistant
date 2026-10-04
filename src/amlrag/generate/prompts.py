"""Prompts and JSON schemas for the two answer modes.

Kept short on purpose: 8-9B local models follow a compact, rule-numbered prompt
more reliably than a long one, and every token here competes with the sources
for the context window.
"""
from __future__ import annotations

from typing import Any

from amlrag.models import Retrieved
from amlrag.retrieve.facts import RULED_OUT_LABELS

# Bump whenever the answer instructions or schemas change. Every answer and every evaluation
# report records it, so runs can be compared knowing which instructions produced them.
#   1: first baseline (results/20261001-031851-full-...)
#   2: typed reasoning (scenario_fact / rule / conclusion), every trigger condition must be met,
#      insufficient_information for an undescribed customer, extracted facts may be wrong,
#      concrete measures, one or two citations per point.
#   3: the unknown-customer check comes first in the method; scenario facts get their own judge
#      prompt; (retrieval, same release) each fact-driven sub-query keeps its best passage.
#   3.1: one retry (RETRY_UNCITED) when an answer cites nothing; seen in E05, where a correct
#      summary came back with an empty key_points list and was withheld.
#   3.2: facts the scenario rules out are shown as established (yes/no/unknown facts), with a rule
#      never to call them unstated; each measure says whether a source requires it or gives it as
#      a risk-based option; a trigger applying does not mean every enhanced measure is required.
#      Found by adversarial tests A01-A03 (data/gold/adversarial.jsonl).
PROMPT_VERSION = "3.2"

RETRY_UNCITED = """Your answer has no points that cite the SOURCES, so it cannot be shown to the user. Return the same JSON object again with the points filled in, each citing the source labels that state it. If the sources really do not answer this, say so as the instructions describe."""

# A determination's reasoning is a chain: facts from the scenario, the rule a source states,
# and the conclusion that applies one to the other. Each kind is checked against its own
# evidence (generate/verify.py): facts against the scenario, rules against the cited passages,
# conclusions against both.
POINT_KINDS = ["scenario_fact", "rule", "conclusion"]

_REASON = {
    "type": "object",
    "properties": {"kind": {"type": "string", "enum": POINT_KINDS}, "point": {"type": "string"},
                   "sources": {"type": "array", "items": {"type": "string"}}},
    "required": ["kind", "point", "sources"],
}

_POINT = {
    "type": "object",
    "properties": {"point": {"type": "string"}, "sources": {"type": "array", "items": {"type": "string"}}},
    "required": ["point", "sources"],
}
_MEASURE = {
    "type": "object",
    "properties": {"measure": {"type": "string"}, "required": {"type": "boolean"},
                   "sources": {"type": "array", "items": {"type": "string"}}},
    "required": ["measure", "required", "sources"],
}

DETERMINE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "tier": {"type": "string", "enum": ["simplified", "standard", "enhanced", "insufficient_information"]},
        "summary": {"type": "string"},
        "reasoning": {"type": "array", "items": _REASON},
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
- Cite source labels exactly as written, e.g. "S2", and only labels that appear in SOURCES. Cite the one or two sources that state the point itself, not sources that merely mention the topic.
- State a rule as narrowly as the source states it, with all of its conditions. Never add conditions, exceptions, examples or consequences the source does not state.
- Write for a new compliance team member: plain English, short sentences, explain any legal term you use.
- confidence: "high" only if a source states the rule directly for this situation; "medium" if you applied a general rule; "low" otherwise."""

_TIERS = """Tiers:
- "enhanced": the sources require enhanced CDD in this situation.
- "simplified": the sources permit simplified CDD AND the scenario meets every condition the sources set (for example low ML/TF risk and no enhanced CDD trigger).
- "standard": ordinary initial CDD applies, with neither simplification nor enhancement.
- "insufficient_information": the sources or the scenario do not let you decide. List what is missing in missing_information."""

_METHOD = """Method:
1. If the scenario does not say who or what the customer is (an individual, a company, a trust and so on), the tier is "insufficient_information". Stop here: "standard" is not a default for an unknown customer.
2. Check the sources for enhanced CDD triggers that match the scenario. A trigger applies only when the scenario meets every condition the source sets: a trigger that needs the ML/TF risk to be high does not apply when the risk is medium, low or not stated. If a trigger applies, the tier is "enhanced", even if the customer would otherwise qualify for simplified CDD.
3. Otherwise check whether the scenario meets every condition the sources set for simplified CDD, read as the source writes it. If a condition is not met or not shown, simplified CDD does not apply.
4. Otherwise the tier is "standard"."""

_REASONING = """- reasoning: 3-6 points that build the decision in order, each with a kind:
  "scenario_fact": a fact from the scenario that matters to the decision, close to the scenario's own words. sources: [].
  "rule": what a source says that decides this situation. sources: the one or two passages that state it.
  "conclusion": how the rule applies to the facts, ending with the tier. sources: the rule passages it applies.
  Give the facts first, then the deciding rule, then the conclusion. Don't discuss rules or tiers that don't apply unless a source says why they don't."""

DETERMINE_SYSTEM = f"""You help compliance officers at an Australian AML/CTF reporting entity decide which customer due diligence (CDD) tier applies to a customer scenario. Your sources are AUSTRAC guidance and the AML/CTF Rules 2025.

{_TIERS}

{_METHOD}

Rules:
{_COMMON_RULES}
- The FACTS block was extracted automatically and may be wrong. Where it differs from the SCENARIO, follow the SCENARIO.
- A fact the SCENARIO denies ("is not a PEP", "no links to high-risk countries", "none of them is located there") is established as false. Never say the scenario does not state it, and never list it in missing_information. Payments to, or trade with, a country do not show that anyone is located or formed there.
{_REASONING}
- When a trigger makes enhanced CDD mandatory, say that the trigger applies. Do not say that every enhanced measure is required or that it applies "regardless" of the customer's circumstances: which measures to use depends on the customer's risk.
- required_measures: the concrete steps for this customer at this tier (what to collect, verify, establish or approve), each with its sources and a "required" flag. required: true only when a cited source says the step must be done in this situation; required: false when a source gives it as an example or option to match the customer's risk ("may include", "such as", "could"). "Apply enhanced CDD" is not a measure: say what it involves here."""

EXPLAIN_SYSTEM = f"""You explain Australian AML/CTF customer due diligence obligations to compliance staff, using AUSTRAC guidance and the AML/CTF Rules 2025.

Rules:
{_COMMON_RULES}
- If the sources do not answer the question, set answerable to false, give a one-sentence summary saying so, and leave key_points empty. Never fill the gap from memory.
- A source that only mentions the subject in passing does not answer a question about it. Every number, amount or deadline you give must appear in a cited source.
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
        if k in ("missing_information", "ruled_out") or v in (False, "unknown", "none", None, []):
            continue
        lines.append(f"- {k}: {v}")
    ruled_out = [RULED_OUT_LABELS[k] for k in facts.get("ruled_out") or [] if k in RULED_OUT_LABELS]
    if not lines and not ruled_out:
        return ""
    block = "FACTS (extracted automatically; may be wrong or incomplete; the SCENARIO is authoritative):\n"
    block += "\n".join(lines) if lines else "- (no trigger facts found)"
    if ruled_out:
        block += "\nRuled out by the scenario (established as false, not missing):\n" + \
            "\n".join(f"- {r}" for r in ruled_out)
    return block + "\n\n"


def determine_messages(scenario: str, results: list[Retrieved], facts: dict[str, Any] | None):
    sources, label_map = source_block(results)
    user = (f"SCENARIO:\n{scenario.strip()}\n\n{_facts_lines(facts)}SOURCES:\n{sources}\n\n"
            "Return the JSON object.")
    return [{"role": "system", "content": DETERMINE_SYSTEM}, {"role": "user", "content": user}], label_map


def explain_messages(question: str, results: list[Retrieved]):
    sources, label_map = source_block(results)
    user = f"QUESTION:\n{question.strip()}\n\nSOURCES:\n{sources}\n\nReturn the JSON object."
    return [{"role": "system", "content": EXPLAIN_SYSTEM}, {"role": "user", "content": user}], label_map


JUDGE_SYSTEM = """You check whether a claim is fully supported by the evidence given.
Answer supported=true only if the evidence states or directly entails every part of the claim. Facts about the customer may come from the SCENARIO; rules and obligations must come from the PASSAGES. Missing detail, a different condition, or an extra requirement means supported=false."""

JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"supported": {"type": "boolean"}, "reason": {"type": "string"}},
    "required": ["supported", "reason"],
}


FACT_JUDGE_SYSTEM = """You check whether a statement about a customer scenario is stated in, or directly implied by, the SCENARIO.
Paraphrase is fine, and so is a correct label for something the scenario describes. Answer supported=false only if the statement adds a fact the scenario does not give or contradicts it."""


def judge_messages(claim: str, passages: list[str], scenario: str | None = None):
    if scenario and not passages:   # a fact restated from the scenario
        return [{"role": "system", "content": FACT_JUDGE_SYSTEM},
                {"role": "user", "content": f"STATEMENT:\n{claim}\n\nSCENARIO:\n{scenario.strip()}\n\n"
                                            "Return the JSON object."}]
    parts = [f"CLAIM:\n{claim}"]
    if scenario:
        parts.append(f"SCENARIO:\n{scenario.strip()}")
    if passages:
        parts.append("PASSAGES:\n" + "\n\n".join(f"[P{i}] {p}" for i, p in enumerate(passages, start=1)))
    return [{"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": "\n\n".join(parts) + "\n\nReturn the JSON object."}]


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

_CLOSED_METHOD = (_METHOD.replace("Check the sources for", "Check for")
                  .replace("the source sets", "the law sets").replace("the sources set", "the law sets")
                  .replace("read as the source writes it", "read as the law states it"))

CLOSED_DETERMINE_SYSTEM = f"""You help compliance officers at an Australian AML/CTF reporting entity decide which customer due diligence (CDD) tier applies to a customer scenario.

{_CLOSED_TIERS}

{_CLOSED_METHOD}

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
