"""Chroma vector store: build from chunks.jsonl, query with pre-computed embeddings."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import chromadb

from amlrag.models import Chunk

log = logging.getLogger(__name__)

MANIFEST = "index_manifest.json"


class IndexMismatch(RuntimeError):
    pass


def _client(chroma_dir: Path) -> chromadb.ClientAPI:
    chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_dir),
                                     settings=chromadb.Settings(anonymized_telemetry=False))


def chunks_digest(chunks: list[Chunk]) -> str:
    h = hashlib.sha256()
    for c in chunks:
        h.update(c.chunk_id.encode())
        h.update(hashlib.sha256(c.text.encode()).digest())
    return h.hexdigest()[:16]


def build_index(chunks: list[Chunk], embedder, chroma_dir: Path, collection: str,
                snapshot: str | None = None, progress=None) -> dict[str, Any]:
    client = _client(chroma_dir)
    try:
        client.delete_collection(collection)
    except Exception:  # collection did not exist
        pass
    col = client.create_collection(collection, embedding_function=None, metadata={"hnsw:space": "cosine"})
    dim = None
    batch = 64
    for i in range(0, len(chunks), batch):
        part = chunks[i:i + batch]
        vecs = embedder.embed_documents([c.embed_text() for c in part])
        dim = dim or len(vecs[0])
        col.add(ids=[c.chunk_id for c in part], embeddings=vecs, documents=[c.text for c in part],
                metadatas=[c.chroma_metadata() for c in part])
        if progress:
            progress(min(i + batch, len(chunks)), len(chunks))
    manifest = {
        "collection": collection,
        "embedder": embedder.name,
        "dim": dim,
        "chunks": len(chunks),
        "chunks_digest": chunks_digest(chunks),
        "snapshot": snapshot,
        "built_at": datetime.now(timezone.utc).isoformat(),
    }
    (chroma_dir / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def read_manifest(chroma_dir: Path) -> dict[str, Any] | None:
    p = chroma_dir / MANIFEST
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


class VectorStore:
    def __init__(self, chroma_dir: Path, collection: str, embedder, chunks: list[Chunk]):
        manifest = read_manifest(chroma_dir)
        if manifest is None:
            raise IndexMismatch(f"No index at {chroma_dir}. Run `amlrag build` first.")
        if manifest["embedder"] != embedder.name:
            raise IndexMismatch(
                f"Index was built with {manifest['embedder']} but the configured embedder is {embedder.name}. "
                "Rebuild with `amlrag build`.")
        if manifest["chunks_digest"] != chunks_digest(chunks):
            raise IndexMismatch("chunks.jsonl changed since the index was built. Rebuild with `amlrag build`.")
        self.manifest = manifest
        self.embedder = embedder
        self.col = _client(chroma_dir).get_collection(collection, embedding_function=None)

    def query(self, text: str, k: int) -> list[tuple[str, float]]:
        """Return (chunk_id, cosine similarity) best-first."""
        vec = self.embedder.embed_query(text)
        res = self.col.query(query_embeddings=[vec], n_results=k, include=["distances"])
        ids = res["ids"][0]
        dists = res["distances"][0]
        return [(cid, 1.0 - float(d)) for cid, d in zip(ids, dists)]
