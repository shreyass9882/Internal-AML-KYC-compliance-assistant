"""Scenario fact extraction and fact-driven sub-queries.

An 8B model reading a long scenario can miss a single decisive fact (a
beneficial owner who is a foreign PEP, a FATF call-for-action country). We ask
the model to pull out a fixed set of CDD-relevant facts first, then turn each
positive fact into a targeted retrieval query so the decisive rule is in the
context window. The same facts feed the guardrails in generate/guardrails.py.
"""
from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

CUSTOMER_TYPES = ["individual", "sole_trader", "company", "partnership", "trust", "unincorporated_association",
                  "government_body", "other", "unknown"]

FACTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "customer_type": {"type": "string", "enum": CUSTOMER_TYPES},
        "pep_status": {"type": "string", "enum": ["none", "domestic", "foreign", "international_organisation", "unknown"]},
        "pep_same_country_foreign_branch": {"type": "boolean"},
        "high_risk_jurisdiction": {"type": "boolean"},
        "suspicious_matter_continuing": {"type": "boolean"},
        "nested_services": {"type": "boolean"},
        "unusual_transaction": {"type": "boolean"},
        "virtual_assets_with_cash": {"type": "boolean"},
        "regulated_or_government": {"type": "boolean"},
        "ml_tf_risk": {"type": "string", "enum": ["low", "medium", "high", "unknown"]},
        "delayed_verification": {"type": "boolean"},
        "missing_information": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["customer_type", "pep_status", "pep_same_country_foreign_branch", "high_risk_jurisdiction",
                 "suspicious_matter_continuing", "nested_services", "unusual_transaction",
                 "virtual_assets_with_cash", "regulated_or_government", "ml_tf_risk", "delayed_verification",
                 "missing_information"],
}

FACTS_SYSTEM = """You extract facts from a customer scenario for an Australian AML/CTF compliance team.
Record only what the scenario states or directly implies. Never guess: use "unknown" or false when the scenario is silent.
Field meanings:
- customer_type: the legal form of the customer.
- pep_status: the most serious politically exposed person status of the customer OR any beneficial owner, person acting on the customer's behalf, or immediate family member / close associate mentioned.
- pep_same_country_foreign_branch: true only if a foreign PEP is served by the reporting entity's branch located in that PEP's own country.
- high_risk_jurisdiction: customer is physically present in, formed in, or transacting with a country the scenario says is high risk or subject to a FATF call for action.
- suspicious_matter_continuing: a suspicious matter report (SMR) was, or must be, submitted and the relationship continues.
- nested_services: the customer is a financial institution / remitter whose own customers' transactions pass through the service.
- unusual_transaction: the scenario says the transaction or structure is unusually large or complex, or has no apparent business or lawful purpose.
- virtual_assets_with_cash: a virtual asset service funded with physical cash.
- regulated_or_government: customer is a government body, APRA/ASIC-licensed regulated entity, listed company, or strata owners corporation.
- ml_tf_risk: the risk rating the scenario gives (or clearly describes).
- delayed_verification: the scenario asks about providing the service before verification is complete.
- missing_information: facts a compliance officer would need but the scenario does not give (short phrases)."""


def facts_messages(scenario: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": FACTS_SYSTEM},
            {"role": "user", "content": f"Return the facts as JSON.\n\nSCENARIO:\n{scenario.strip()}"}]


def normalise_facts(raw: dict[str, Any]) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    for key, spec in FACTS_SCHEMA["properties"].items():
        val = raw.get(key)
        if spec["type"] == "boolean":
            facts[key] = bool(val) if isinstance(val, bool) else str(val).lower() == "true"
        elif spec["type"] == "array":
            facts[key] = [str(v) for v in val] if isinstance(val, list) else []
        else:
            allowed = spec.get("enum")
            facts[key] = val if (not allowed or val in allowed) else "unknown"
    return facts


def extract_facts(llm, scenario: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        raw, stats = llm.chat_json(facts_messages(scenario), FACTS_SCHEMA, task="facts")
        return normalise_facts(raw), stats
    except Exception as exc:  # fact extraction is an enhancement; never fatal
        log.warning("fact extraction failed: %s", exc)
        return None, {"error": str(exc)}


_CTYPE_QUERY = {
    "individual": "initial customer due diligence individual KYC information verify identity",
    "sole_trader": "initial customer due diligence sole trader KYC ABN business name",
    "company": "initial customer due diligence body corporate company beneficial owners directors",
    "partnership": "initial customer due diligence partnership partners beneficial owners",
    "trust": "initial customer due diligence trust trustee settlor beneficiaries appointor",
    "unincorporated_association": "initial customer due diligence unincorporated association senior managing official",
    "government_body": "initial customer due diligence government body evidence of existence",
}


def sub_queries(facts: dict[str, Any] | None) -> list[str]:
    """Targeted retrieval queries implied by the extracted facts (never answers)."""
    if not facts:
        return []
    q: list[str] = []
    if facts.get("customer_type") in _CTYPE_QUERY:
        q.append(_CTYPE_QUERY[facts["customer_type"]])
    pep = facts.get("pep_status")
    if pep == "foreign":
        q.append("foreign politically exposed person enhanced customer due diligence source of wealth source of funds")
        if facts.get("pep_same_country_foreign_branch"):
            q.append("foreign branch politically exposed person same country treated as domestic politically exposed person")
    elif pep in ("domestic", "international_organisation"):
        q.append(f"{pep.replace('_', ' ')} politically exposed person high ML/TF risk enhanced customer due diligence")
    if facts.get("high_risk_jurisdiction"):
        q.append("high-risk jurisdiction FATF call for action enhanced customer due diligence")
    if facts.get("suspicious_matter_continuing"):
        q.append("suspicious matter report continue business relationship enhanced customer due diligence")
    if facts.get("nested_services"):
        q.append("nested services relationship initial due diligence shell bank")
    if facts.get("unusual_transaction"):
        q.append("unusually large or complex transaction no apparent business or lawful purpose enhanced customer due diligence")
    if facts.get("virtual_assets_with_cash"):
        q.append("virtual asset service cash source of funds enhanced customer due diligence")
    if facts.get("regulated_or_government"):
        q.append("simplified customer due diligence beneficial owners government body regulated entity listed company")
    if facts.get("ml_tf_risk") == "low" and not q[1:]:
        q.append("simplified customer due diligence low ML/TF risk conditions")
    if facts.get("ml_tf_risk") == "high":
        q.append("high ML/TF risk customer enhanced customer due diligence measures")
    if facts.get("delayed_verification"):
        q.append("delayed initial customer due diligence verification after providing designated service")
    return q
