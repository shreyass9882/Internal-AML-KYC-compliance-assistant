"""Core data structures shared across ingestion, retrieval and generation."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Section:
    """A logically complete unit of a source document (a rule section or a guidance heading)."""

    doc_id: str
    doc_title: str
    kind: str                      # "legislation" | "guidance"
    section_key: str               # "6-23" for legislation; heading slug for guidance
    heading_path: list[str]        # ["Part 6—Customer due diligence", "Division 5—...", "6-23 Initial CDD—PEPs"]
    text: str
    url: str | None = None
    section_title: str = ""
    doc_short: str = ""
    section_label: str = "s"
    last_updated: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Chunk:
    chunk_id: str                  # "<doc_id>::<section_key>::<n>" (stable across rebuilds of the same snapshot)
    doc_id: str
    section_key: str
    citation: str                  # human-readable label shown to users
    heading_path: str
    text: str
    url: str | None
    kind: str
    position: int                  # index of this chunk within its section
    word_count: int
    last_updated: str | None = None

    @property
    def section_ref(self) -> str:
        return f"{self.doc_id}::{self.section_key}"

    def embed_text(self) -> str:
        """Text sent to the embedder: a contextual header plus the body.

        Prepending the document and heading path lets short chunks such as a
        list of KYC fields still match queries that name the customer type.
        """
        return f"{self.citation}\n{self.heading_path}\n\n{self.text}"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Chunk":
        fields = {k: d.get(k) for k in cls.__dataclass_fields__}
        return cls(**fields)

    def chroma_metadata(self) -> dict[str, Any]:
        # Chroma metadata values must be scalars; None is not allowed.
        meta = {
            "doc_id": self.doc_id,
            "section_key": self.section_key,
            "citation": self.citation,
            "heading_path": self.heading_path,
            "url": self.url or "",
            "kind": self.kind,
            "position": self.position,
            "word_count": self.word_count,
            "last_updated": self.last_updated or "",
        }
        return meta


@dataclass
class Retrieved:
    chunk: Chunk
    rrf_score: float = 0.0
    dense_similarity: float | None = None
    bm25_score: float | None = None
    matched_queries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "citation": self.chunk.citation,
            "url": self.chunk.url,
            "rrf_score": round(self.rrf_score, 5),
            "dense_similarity": None if self.dense_similarity is None else round(self.dense_similarity, 4),
            "bm25_score": None if self.bm25_score is None else round(self.bm25_score, 3),
            "matched_queries": self.matched_queries,
        }


def ref_matches(chunk_id: str, ref: str) -> bool:
    """True if a chunk id falls under a gold reference.

    A reference is a document id ("austrac-ecdd"), a section ("rules2025::6-23")
    or a chunk. "rules2025::6-2" deliberately does NOT match "rules2025::6-23::0".
    """
    return chunk_id == ref or chunk_id.startswith(ref + "::")
