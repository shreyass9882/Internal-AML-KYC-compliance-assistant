"""Hybrid retrieval: dense (Chroma) + BM25, fused with weighted reciprocal rank fusion."""
from __future__ import annotations

from collections import defaultdict

from amlrag.index.store import VectorStore
from amlrag.models import Chunk, Retrieved
from amlrag.retrieve.bm25 import BM25Index


class Retriever:
    def __init__(self, chunks: list[Chunk], store: VectorStore, dense_k: int = 20, bm25_k: int = 20,
                 final_k: int = 8, rrf_k: int = 60, max_chunks_per_section: int = 2, use_hybrid: bool = True):
        self.chunks = {c.chunk_id: c for c in chunks}
        self.store = store
        self.bm25 = BM25Index(chunks) if use_hybrid else None
        self.dense_k = dense_k
        self.bm25_k = bm25_k
        self.final_k = final_k
        self.rrf_k = rrf_k
        self.max_per_section = max_chunks_per_section

    @classmethod
    def from_config(cls, chunks: list[Chunk], store: VectorStore, r) -> "Retriever":
        return cls(chunks, store, r.dense_k, r.bm25_k, r.final_k, r.rrf_k, r.max_chunks_per_section, r.use_hybrid)

    def search(self, primary: str, extra_queries: list[str] | None = None, k: int | None = None) -> list[Retrieved]:
        """Fuse rankings from every (query, retriever) pair.

        The user's own text has weight 1.0; fact-derived sub-queries 0.8, so
        they add evidence without drowning out the scenario itself.
        """
        k = k or self.final_k
        queries = [(primary, 1.0)] + [(q, 0.8) for q in dict.fromkeys(extra_queries or []) if q.strip()]
        fused: dict[str, float] = defaultdict(float)
        own: dict[str, dict[str, float]] = {q: defaultdict(float) for q, _ in queries}  # each query's own scores
        dense_best: dict[str, float] = {}
        bm25_best: dict[str, float] = {}
        matched: dict[str, list[str]] = defaultdict(list)

        for q, w in queries:
            for rank, (cid, sim) in enumerate(self.store.query(q, self.dense_k)):
                if cid not in self.chunks:
                    continue
                fused[cid] += w / (self.rrf_k + rank + 1)
                own[q][cid] += 1 / (self.rrf_k + rank + 1)
                dense_best[cid] = max(sim, dense_best.get(cid, -1.0))
                if q not in matched[cid]:
                    matched[cid].append(q)
            if self.bm25 is not None:
                for rank, (cid, score) in enumerate(self.bm25.query(q, self.bm25_k)):
                    fused[cid] += w / (self.rrf_k + rank + 1)
                    own[q][cid] += 1 / (self.rrf_k + rank + 1)
                    bm25_best[cid] = max(score, bm25_best.get(cid, 0.0))
                    if q not in matched[cid]:
                        matched[cid].append(q)

        # Every sub-query keeps its own best passage. Without this, passages that several queries
        # agree on (e.g. source of wealth for PEPs) crowded out the one passage a single targeted
        # query was looking for (e.g. when enhanced CDD must be applied), and the answer then
        # justified the tier from the wrong rule.
        reserved: list[str] = []
        for q, _ in queries[1:]:
            if own[q]:
                best = max(own[q].items(), key=lambda kv: kv[1])[0]
                if best not in reserved:
                    reserved.append(best)
        ranked = sorted(fused.items(), key=lambda kv: -kv[1])
        order = reserved[:k] + [cid for cid, _ in ranked if cid not in reserved]

        per_section: dict[str, int] = defaultdict(int)
        picked: list[str] = []
        for cid in order:
            chunk = self.chunks[cid]
            if per_section[chunk.section_ref] >= self.max_per_section:
                continue
            per_section[chunk.section_ref] += 1
            picked.append(cid)
            if len(picked) >= k:
                break
        picked.sort(key=lambda cid: -fused[cid])   # present the sources best-first
        return [Retrieved(chunk=self.chunks[cid], rrf_score=fused[cid], dense_similarity=dense_best.get(cid),
                          bm25_score=bm25_best.get(cid),
                          matched_queries=["primary" if m == primary else m for m in matched[cid]])
                for cid in picked]

    @staticmethod
    def max_similarity(results: list[Retrieved]) -> float:
        sims = [r.dense_similarity for r in results if r.dense_similarity is not None]
        return max(sims) if sims else 0.0
