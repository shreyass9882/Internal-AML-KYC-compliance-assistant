"""Scenario fact extraction and fact-driven sub-queries.

An 8B model reading a long scenario can miss a single decisive fact (a
beneficial owner who is a foreign PEP, a FATF call-for-action country). We ask
the model to pull out a fixed set of CDD-relevant facts first, then turn each
positive fact into a targeted retrieval query so the decisive rule is in the
context window. The same facts feed the guardrails in generate/guardrails.py.

The PEP and customer-type descriptions in FACTS_SYSTEM paraphrase AUSTRAC's PEP and
initial-CDD guidance (all in the knowledge base). They only steer retrieval and the
guardrails; the answer itself must still cite a retrieved source. Without them the
first baseline run left pep_status "unknown" for a foreign MP, judge and minister
and labelled an Australian MP "foreign".

The trigger facts are three-way (yes / no / unknown) since prompt v3.2. As plain booleans,
"the scenario says the owners are NOT in that country" and "the scenario doesn't say" both
became false, and an answer then claimed the scenario "does not state" where the owners were.
The booleans downstream code reads are unchanged (yes = True); facts["ruled_out"] lists the
triggers the scenario explicitly rules out, so the answer prompt and the checks can treat them
as established, not missing.
"""
from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)

# Trigger facts answered yes / no / unknown; normalise_facts turns them into booleans (yes = True)
# and lists the "no" ones in facts["ruled_out"].
TRISTATE_FACTS = ("pep_same_country_foreign_branch", "high_risk_jurisdiction", "suspicious_matter_continuing",
                  "nested_services", "unusual_transaction", "virtual_assets_with_cash", "regulated_or_government",
                  "delayed_verification")
_TRISTATE = {"type": "string", "enum": ["yes", "no", "unknown"]}

CUSTOMER_TYPES = ["individual", "sole_trader", "company", "partnership", "trust", "unincorporated_association",
                  "government_body", "other", "unknown"]

FACTS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "customer_type": {"type": "string", "enum": CUSTOMER_TYPES},
        "pep_status": {"type": "string", "enum": ["none", "domestic", "foreign", "international_organisation", "unknown"]},
        "pep_same_country_foreign_branch": _TRISTATE,
        "high_risk_jurisdiction": _TRISTATE,
        "suspicious_matter_continuing": _TRISTATE,
        "nested_services": _TRISTATE,
        "unusual_transaction": _TRISTATE,
        "virtual_assets_with_cash": _TRISTATE,
        "regulated_or_government": _TRISTATE,
        "ml_tf_risk": {"type": "string", "enum": ["low", "medium", "high", "unknown"]},
        "delayed_verification": _TRISTATE,
        "missing_information": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["customer_type", "pep_status", "pep_same_country_foreign_branch", "high_risk_jurisdiction",
                 "suspicious_matter_continuing", "nested_services", "unusual_transaction",
                 "virtual_assets_with_cash", "regulated_or_government", "ml_tf_risk", "delayed_verification",
                 "missing_information"],
}

FACTS_SYSTEM = """You extract facts from a customer scenario for an Australian AML/CTF compliance team.
Classify what the scenario describes, even when it doesn't use the legal term: "a member of a foreign national
parliament" is a foreign PEP and "XYZ Pty Ltd" is a company, although neither word appears.
For the yes/no fields: "yes" when the scenario says or clearly describes it; "no" when the scenario says it is not so
or rules it out ("not a PEP", "no links to high-risk countries", "none of them lives there"); "unknown" only when the
scenario says nothing about it. "No" and "unknown" are different: never use "unknown" for a fact the scenario denies.

Field meanings:
- customer_type: the legal form of the customer, the person or entity the service is for.
  individual: a person acting for themselves (including a minister or official opening a personal account).
  sole_trader: an individual running a business in their own name. company: a Pty Ltd, Ltd or listed company.
  partnership. trust: any trust (family, discretionary, unit, testamentary, charitable, self-managed super fund)
  or a trustee acting for one. unincorporated_association: a club, residents' association, church or community
  group that is not incorporated. government_body: a government department, agency, local council, embassy or
  state-owned enterprise. other: anything else, such as a strata owners corporation.
- pep_status: the most serious politically exposed person (PEP) status of the customer, any beneficial owner, any
  person acting on the customer's behalf (such as a signatory or trustee) or any person on whose behalf the
  customer receives the service (such as a trust beneficiary). "none" only if the scenario says nobody is a PEP.
  foreign: someone who holds a prominent public position in or for a country other than Australia: head of state or
  government, minister or deputy minister, member of a legislature, senior judge, ambassador or high commissioner,
  high-ranking military officer, head or board member of a government body or state-owned company, or member of a
  political party's governing body; also their family members and close business associates.
  domestic: the same kinds of position in Australia: member of the Commonwealth, a state or a territory parliament,
  Governor-General or Governor, senior judge, head of a government department or agency, head of a local council,
  Australia's ambassadors and high commissioners, the most senior defence officers; also their family members and
  close associates. international_organisation: a senior official of an international organisation (such as the
  UN, IMF or World Bank).
- pep_same_country_foreign_branch: yes only if the reporting entity's own branch in a foreign country serves a
  foreign PEP whose PEP status comes from that same country.
- high_risk_jurisdiction: the customer, a beneficial owner or a person acting for the customer is physically present
  in, or formed in, a country the scenario says is high risk or subject to a FATF call for action, or a country you
  know is on the FATF call-for-action list. Sending payments to, buying from or trading with a country does not count
  on its own. A country under FATF increased monitoring (the "grey list") is not a call-for-action country.
- suspicious_matter_continuing: a suspicious matter report (SMR) was, or must be, submitted and the relationship continues.
- nested_services: the customer is a financial institution or remitter whose own customers' transactions pass through the service.
- unusual_transaction: the scenario says the transaction or structure is unusually large or complex, or has no apparent business or lawful purpose.
- virtual_assets_with_cash: a virtual asset service funded with physical cash.
- regulated_or_government: the customer is, or is controlled by, a government body, a listed public company, a
  strata owners corporation, or an entity licensed or registered as a bank, insurer, APRA-regulated super fund or
  financial services licensee.
- ml_tf_risk: the risk rating the scenario gives or clearly describes. Don't infer it from PEP status alone.
- delayed_verification: the scenario asks about providing the service before verification is complete.
- missing_information: up to three facts that are not in the scenario and would change the CDD tier (short phrases).
  Leave it empty when the scenario has what is needed."""


# How a ruled-out fact is shown to the answer model, and the words that show a sentence is about it.
# Each entry is a tuple of term groups; a text is about the fact when every group has a match.
RULED_OUT_LABELS: dict[str, str] = {
    "pep": "a politically exposed person (PEP) among the customer, its owners, agents or beneficiaries",
    "high_risk_jurisdiction": "the customer, a beneficial owner or an agent being in, or formed in, a FATF "
                              "call-for-action country",
    "suspicious_matter_continuing": "a suspicious matter report with the relationship continuing",
    "nested_services": "a nested services relationship",
    "unusual_transaction": "an unusually large or complex transaction with no clear purpose",
    "virtual_assets_with_cash": "a virtual asset service funded with cash",
    "regulated_or_government": "the customer being a government body, listed company or regulated entity",
    "delayed_verification": "verification delayed until after the service starts",
    "pep_same_country_foreign_branch": "a foreign branch serving a PEP from its own country",
}
RULED_OUT_TERMS: dict[str, tuple[tuple[str, ...], ...]] = {
    "pep": (("pep", "politically exposed", "politician", "public official"),),
    "high_risk_jurisdiction": (("jurisdiction", "country", "countries", "fatf"),
                               ("located", "formed", "resident", "lives", "live in", "present", "incorporated",
                                "based in", "physically")),
    "suspicious_matter_continuing": (("suspicious matter", "smr"),),
    "nested_services": (("nested",),),
    "unusual_transaction": (("unusual",),),
    "virtual_assets_with_cash": (("virtual asset", "crypto", "digital currency"),),
    "delayed_verification": (("delay",),),
}


def mentions_fact(text: str, key: str) -> bool:
    """True when the text is about the given fact (every term group of RULED_OUT_TERMS[key] matches)."""
    groups = RULED_OUT_TERMS.get(key)
    low = text.lower()
    return bool(groups) and all(any(t in low for t in group) for group in groups)


def facts_messages(scenario: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": FACTS_SYSTEM},
            {"role": "user", "content": f"Return the facts as JSON.\n\nSCENARIO:\n{scenario.strip()}"}]


def tristate(val: Any) -> str:
    """yes / no / unknown from a model value.

    A boolean (the pre-3.2 schema, and the offline stub) cannot tell "the scenario denies it" from
    "the scenario doesn't say", so False counts as unknown: only an explicit "no" rules a fact out.
    """
    if val is True or str(val).strip().lower() in ("yes", "true"):
        return "yes"
    if str(val).strip().lower() == "no":
        return "no"
    return "unknown"


def normalise_facts(raw: dict[str, Any]) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    ruled_out: list[str] = []
    for key, spec in FACTS_SCHEMA["properties"].items():
        val = raw.get(key)
        if key in TRISTATE_FACTS:
            state = tristate(val)
            facts[key] = state == "yes"
            if state == "no":
                ruled_out.append(key)
        elif spec["type"] == "boolean":
            facts[key] = bool(val) if isinstance(val, bool) else str(val).lower() == "true"
        elif spec["type"] == "array":
            facts[key] = [str(v) for v in val] if isinstance(val, list) else []
        else:
            allowed = spec.get("enum")
            facts[key] = val if (not allowed or val in allowed) else "unknown"
    if facts.get("pep_status") == "none":
        ruled_out.insert(0, "pep")
    facts["ruled_out"] = ruled_out
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


_PEP_OBLIGATIONS_QUERY = ("politically exposed person senior manager approval before providing designated service "
                          "source of wealth source of funds")


def sub_queries(facts: dict[str, Any] | None) -> list[str]:
    """Targeted retrieval queries implied by the extracted facts (never answers)."""
    if not facts:
        return []
    q: list[str] = []
    if facts.get("customer_type") in _CTYPE_QUERY:
        q.append(_CTYPE_QUERY[facts["customer_type"]])
    pep = facts.get("pep_status")
    if pep == "foreign":
        # The trigger (when enhanced CDD must be applied) and the PEP-specific obligations are
        # separate passages; one combined query let the source-of-wealth passages crowd out the
        # trigger, so answers justified the tier from a consequence rather than the rule.
        q.append("when you must apply enhanced customer due diligence foreign politically exposed person")
        q.append(_PEP_OBLIGATIONS_QUERY)
        if facts.get("pep_same_country_foreign_branch"):
            q.append("foreign branch politically exposed person same country treated as domestic politically exposed person")
    elif pep in ("domestic", "international_organisation"):
        q.append(f"enhanced CDD obligations for politically exposed persons {pep.replace('_', ' ')} PEP high ML/TF risk")
        if facts.get("ml_tf_risk") == "high":  # these obligations only attach at high risk
            q.append(_PEP_OBLIGATIONS_QUERY)
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
