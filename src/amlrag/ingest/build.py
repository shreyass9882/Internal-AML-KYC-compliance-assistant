"""Parse every snapshotted source into sections, then chunks (JSONL on disk)."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from amlrag.config import Config
from amlrag.ingest.chunk import chunk_sections
from amlrag.ingest.fetch import all_docs, load_lock, raw_path_for
from amlrag.ingest.parse_html import parse_guidance_html
from amlrag.ingest.parse_legislation import parse_legislation_file
from amlrag.models import Chunk, Section

log = logging.getLogger(__name__)


def parse_all(cfg: Config) -> tuple[list[Section], list[str]]:
    sections: list[Section] = []
    missing: list[str] = []
    lock = load_lock(cfg)
    for doc in all_docs(cfg):
        path = raw_path_for(cfg, doc)
        if path is None:
            if not doc.optional:
                missing.append(doc.id)
            continue
        url = doc.url or lock.get("documents", {}).get(doc.id, {}).get("url")
        if doc.kind == "legislation":
            if not doc.section_pattern:
                raise ValueError(f"{doc.id}: legislation needs section_pattern in kb/sources.yaml")
            secs = parse_legislation_file(path, doc.id, doc.title, doc.short, doc.section_pattern,
                                          doc.section_label, doc.include_parts, url, doc.include_sections)
        elif path.suffix.lower() in (".html", ".htm"):
            secs = parse_guidance_html(path.read_bytes(), doc.id, doc.title, url)
        else:
            log.warning("%s: unsupported file type %s for guidance; skipped", doc.id, path.suffix)
            continue
        if not secs:
            log.warning("%s: parsed 0 sections from %s (check the parser against this file)", doc.id, path)
        sections.extend(secs)
    return sections, missing


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_chunks(path: Path) -> list[Chunk]:
    with open(path, encoding="utf-8") as fh:
        return [Chunk.from_dict(json.loads(line)) for line in fh if line.strip()]


def build_chunks(cfg: Config) -> dict:
    sections, missing = parse_all(cfg)
    ck = cfg.chunking
    chunks = chunk_sections(sections, ck.max_words, ck.overlap_words, ck.min_words)
    write_jsonl(cfg.path("sections_file"), [s.to_dict() for s in sections])
    write_jsonl(cfg.path("chunks_file"), [c.to_dict() for c in chunks])
    per_doc: dict[str, int] = {}
    for c in chunks:
        per_doc[c.doc_id] = per_doc.get(c.doc_id, 0) + 1
    return {"sections": len(sections), "chunks": len(chunks), "per_doc": per_doc, "missing": missing}
