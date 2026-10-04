"""Guardrails against under-applying CDD.

Under-applying CDD (standard or simplified where enhanced is mandatory) is the
costly error for a compliance team; over-applying costs effort, not a breach.
These checks compare the model's tier with the facts it extracted from the
scenario. They never invent a legal basis: an escalation is made only when a
retrieved source contains the trigger, and that source is cited.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from amlrag.models import Retrieved


@dataclass(frozen=True)
class Trigger:
    key: str
    label: str
    applies: Callable[[dict[str, Any]], bool]
    evidence_terms: tuple[tuple[str, ...], ...]   # any group whose terms ALL appear in a source = evidence


ECDD_TRIGGERS: tuple[Trigger, ...] = (
    Trigger("foreign_pep", "a foreign politically exposed person is involved",
            lambda f: f.get("pep_status") == "foreign" and not f.get("pep_same_country_foreign_branch"),
            (("foreign politically exposed",), ("foreign pep",))),
    Trigger("high_risk_jurisdiction", "the customer is connected to a high-risk jurisdiction",
            lambda f: bool(f.get("high_risk_jurisdiction")),
            (("call for action",), ("high-risk", "jurisdiction"), ("high risk", "country"), ("high-risk", "country"))),
    Trigger("smr_continuing", "a suspicious matter report was given and the relationship continues",
            lambda f: bool(f.get("suspicious_matter_continuing")),
            (("suspicious matter", "enhanced"),)),
    Trigger("nested_services", "the service is a nested services relationship",
            lambda f: bool(f.get("nested_services")),
            (("nested",),)),
    Trigger("unusual_transaction", "the transaction is unusually large or complex, or lacks a clear purpose",
            lambda f: bool(f.get("unusual_transaction")),
            (("unusual",), ("complex", "enhanced"), ("no apparent", "purpose"), ("no clear", "purpose"))),
    Trigger("high_risk", "the customer's ML/TF risk is rated high",
            lambda f: f.get("ml_tf_risk") == "high",
            (("high", "enhanced customer due diligence"), ("high", "enhanced cdd"), ("high", "ecdd"))),
)


def _evidence(trigger: Trigger, label_map: dict[str, Retrieved]) -> str | None:
    for label, r in label_map.items():
        text = f"{r.chunk.heading_path} {r.chunk.text}".lower()
        if any(all(term in text for term in group) for group in trigger.evidence_terms):
            return label
    return None


def apply_guardrails(tier: str, facts: dict[str, Any] | None, label_map: dict[str, Retrieved],
                     mode: str = "escalate") -> dict[str, Any]:
    """Return {"tier", "warnings", "escalated", "added_points", "fired"}."""
    result: dict[str, Any] = {"tier": tier, "warnings": [], "escalated": False, "added_points": [], "fired": []}
    if not facts:
        return result
    fired = [t for t in ECDD_TRIGGERS if t.applies(facts)]
    result["fired"] = [t.key for t in fired]

    if fired and tier != "enhanced":
        for t in fired:
            label = _evidence(t, label_map)
            msg = (f"The scenario indicates {t.label}, which is an enhanced CDD trigger, but the model "
                   f"determined '{tier.replace('_', ' ')}'.")
            if label and mode == "escalate":
                result["tier"] = "enhanced"
                result["escalated"] = True
                result["added_points"].append({
                    "kind": "conclusion",
                    "point": f"Escalated by guardrail: the scenario indicates {t.label}. The cited source "
                             f"treats this as requiring enhanced CDD. A compliance officer should confirm.",
                    "sources": [label],
                })
                result["warnings"].append(msg + " Escalated to enhanced; please review.")
            elif label:
                result["warnings"].append(msg + " Review before relying on this answer.")
            else:
                result["warnings"].append(msg + " No retrieved source covers this trigger; the knowledge base "
                                          "may be missing the relevant guidance.")
    if result["tier"] == "simplified":
        risk = facts.get("ml_tf_risk")
        if risk in ("medium", "high"):
            result["warnings"].append(
                f"Simplified CDD was suggested but the scenario rates ML/TF risk as {risk}; the sources "
                "generally only permit simplified CDD for low-risk customers.")
            if mode == "escalate":
                result["tier"] = "standard"
                result["escalated"] = True
    return result
