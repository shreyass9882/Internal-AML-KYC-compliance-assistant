"""Lexical retrieval with BM25 (legal text rewards exact terms like "6-23" or "source of wealth")."""
from __future__ import annotations

from rank_bm25 import BM25Okapi

from amlrag.models import Chunk
from amlrag.textutil import expand_abbreviations, tokenize


class BM25Index:
    def __init__(self, chunks: list[Chunk]):
        self.ids = [c.chunk_id for c in chunks]
        corpus = [tokenize(f"{c.citation} {c.heading_path} {c.text}") for c in chunks]
        self.bm25 = BM25Okapi(corpus)

    def query(self, text: str, k: int) -> list[tuple[str, float]]:
        toks = tokenize(expand_abbreviations(text))
        if not toks:
            return []
        scores = self.bm25.get_scores(toks)
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        return [(self.ids[i], float(scores[i])) for i in order if scores[i] > 0]
