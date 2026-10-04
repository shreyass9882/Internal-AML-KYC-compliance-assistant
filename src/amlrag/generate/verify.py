"""Post-generation citation checks: every claim must point at a retrieved source that supports it."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from amlrag.generate.prompts import POINT_KINDS
from amlrag.models import Retrieved
from amlrag.textutil import content_words

_LABEL_RE = re.compile(r"(?:S|Source\s*)(\d{1,2})", re.I)


def normalise_label(raw: str) -> str | None:
    m = _LABEL_RE.search(str(raw))
    return f"S{int(m.group(1))}" if m else None


def lexical_support(claim: str, passages: list[str]) -> float:
    """Share of the claim's content words found in the cited passages (0-1)."""
    cw = content_words(claim)
    if not cw:
        return 1.0
    pool: set[str] = set()
    for p in passages:
        pool |= content_words(p)
    return len(cw & pool) / len(cw)


@dataclass
class VerifiedPoint:
    text: str
    labels: list[str]
    invalid_labels: list[str]
    support: float
    supported: bool
    kind: str | None = None   # scenario_fact | rule | conclusion for reasoning points; None otherwise
    required: bool | None = None  # measures only: True = a source requires it here, False = a risk-based option

    @property
    def needs_citation(self) -> bool:
        """A fact taken from the scenario is checked against the scenario, not a source."""
        return self.kind != "scenario_fact"

    def to_dict(self, label_map: dict[str, Retrieved]) -> dict[str, Any]:
        return {
            "text": self.text,
            "kind": self.kind,
            "citations": [
                {"label": l, "chunk_id": label_map[l].chunk.chunk_id, "citation": label_map[l].chunk.citation,
                 "url": label_map[l].chunk.url}
                for l in self.labels
            ],
            "invalid_labels": self.invalid_labels,
            "support": round(self.support, 3),
            "supported": self.supported,
            "required": self.required,
        }


@dataclass
class Verification:
    points: dict[str, list[VerifiedPoint]] = field(default_factory=dict)
    total_labels: int = 0
    valid_labels: int = 0

    @property
    def all_points(self) -> list[VerifiedPoint]:
        return [p for group in self.points.values() for p in group]

    @property
    def citation_validity(self) -> float:
        return 1.0 if self.total_labels == 0 else self.valid_labels / self.total_labels

    @property
    def uncited(self) -> list[VerifiedPoint]:
        return [p for p in self.all_points if p.needs_citation and not p.labels]

    @property
    def unsupported(self) -> list[VerifiedPoint]:
        return [p for p in self.all_points if not p.supported]

    @property
    def cited_labels(self) -> list[str]:
        seen: list[str] = []
        for p in self.all_points:
            for l in p.labels:
                if l not in seen:
                    seen.append(l)
        return seen


def verify(output: dict[str, Any], label_map: dict[str, Retrieved], min_support: float,
           groups: dict[str, str], scenario: str | None = None) -> Verification:
    """groups maps an output key (e.g. "reasoning") to the text field of its items (e.g. "point").

    Each point is checked against its own evidence: a scenario_fact against the scenario, a rule
    against its cited passages, a conclusion against its cited passages plus the scenario (it
    applies one to the other). Points without a kind (measures, key points) need cited passages.
    """
    ver = Verification()
    for key, text_field in groups.items():
        items = output.get(key) or []
        vps: list[VerifiedPoint] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            text = str(item.get(text_field, "")).strip()
            if not text:
                continue
            raw_labels = item.get("sources") or []
            if isinstance(raw_labels, str):
                raw_labels = re.split(r"[,\s]+", raw_labels)
            labels, invalid = [], []
            for raw in raw_labels:
                lab = normalise_label(raw)
                ver.total_labels += 1
                if lab and lab in label_map:
                    ver.valid_labels += 1
                    if lab not in labels:
                        labels.append(lab)
                else:
                    invalid.append(str(raw))
            kind = item.get("kind") if item.get("kind") in POINT_KINDS else None
            passages = [label_map[l].chunk.text for l in labels]
            if kind == "scenario_fact" and scenario:
                support = lexical_support(text, [scenario])
                supported = support >= min_support
            else:
                evidence = passages + ([scenario] if kind == "conclusion" and scenario else [])
                support = lexical_support(text, evidence) if labels else 0.0
                supported = bool(labels) and support >= min_support
            required = item.get("required") if isinstance(item.get("required"), bool) else None
            vps.append(VerifiedPoint(text, labels, invalid, support, supported, kind, required))
        ver.points[key] = vps
    return ver


_CONF_ORDER = {"low": 0, "medium": 1, "high": 2}


def cap_confidence(model_conf: str, ver: Verification, max_unsupported_share: float) -> tuple[str, list[str]]:
    """Confidence can only go down from what the model claims, based on the evidence checks."""
    notes: list[str] = []
    conf = model_conf if model_conf in _CONF_ORDER else "low"
    pts = ver.all_points
    if not pts:
        return "low", ["The answer contains no cited points."]
    if ver.uncited:
        notes.append(f"{len(ver.uncited)} point(s) have no valid citation.")
        conf = "low"
    share = len(ver.unsupported) / len(pts)
    if share > max_unsupported_share:
        notes.append(f"{len(ver.unsupported)} of {len(pts)} point(s) are weakly supported by their cited text.")
        conf = "low"
    elif ver.unsupported and _CONF_ORDER[conf] > 1:
        conf = "medium"
    if ver.citation_validity < 1.0:
        notes.append("The model cited sources that were not retrieved; those citations were removed.")
        conf = min(conf, "medium", key=lambda c: _CONF_ORDER[c])
    return conf, notes
