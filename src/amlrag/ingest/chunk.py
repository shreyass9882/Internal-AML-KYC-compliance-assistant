"""Structure-aware chunking: split sections on paragraph boundaries, never across sections."""
from __future__ import annotations

import re

from amlrag.models import Chunk, Section
from amlrag.textutil import word_count

_SENT_RE = re.compile(r"(?<=[.;:])\s+(?=[A-Z(])")


def citation_label(section: Section) -> str:
    if section.kind == "legislation":
        return f"{section.doc_short}, {section.section_label} {section.section_key} — {section.section_title}"
    title = section.doc_title
    if len(section.heading_path) > 1:
        return f"AUSTRAC guidance: {title} › {section.heading_path[-1]}"
    return f"AUSTRAC guidance: {title}"


def _split_long(paragraph: str, max_words: int) -> list[str]:
    """Split one oversized paragraph at sentence boundaries, then hard-wrap if needed."""
    pieces, cur = [], []
    for sent in _SENT_RE.split(paragraph):
        if cur and word_count(" ".join(cur + [sent])) > max_words:
            pieces.append(" ".join(cur))
            cur = []
        cur.append(sent)
    if cur:
        pieces.append(" ".join(cur))
    out = []
    for p in pieces:
        words = p.split()
        while len(words) > max_words:
            out.append(" ".join(words[:max_words]))
            words = words[max_words:]
        if words:
            out.append(" ".join(words))
    return out


def chunk_section(section: Section, max_words: int = 320, overlap_words: int = 40,
                  min_words: int = 20) -> list[Chunk]:
    paragraphs: list[str] = []
    for para in section.text.split("\n"):
        para = para.strip()
        if not para:
            continue
        paragraphs.extend(_split_long(para, max_words) if word_count(para) > max_words else [para])

    windows: list[list[str]] = []
    cur: list[str] = []
    for para in paragraphs:
        if cur and word_count("\n".join(cur + [para])) > max_words:
            windows.append(cur)
            # Overlap: carry the trailing paragraph (or its tail) into the next window
            # so a list introduced by "the reporting entity must:" keeps its lead-in.
            tail = cur[-1]
            carry = tail if word_count(tail) <= overlap_words else " ".join(tail.split()[-overlap_words:])
            cur = [carry] if overlap_words > 0 else []
        cur.append(para)
    if cur:
        windows.append(cur)

    # Fold a tiny trailing window into its predecessor.
    if len(windows) > 1 and word_count("\n".join(windows[-1])) < min_words:
        tail = windows.pop()
        windows[-1].extend(tail[1:] if overlap_words else tail)

    label = citation_label(section)
    heading = " › ".join(section.heading_path)
    chunks = []
    for i, window in enumerate(windows):
        text = "\n".join(window)
        if word_count(text) < 5:
            continue
        chunks.append(Chunk(
            chunk_id=f"{section.doc_id}::{section.section_key}::{i}",
            doc_id=section.doc_id,
            section_key=section.section_key,
            citation=label,
            heading_path=heading,
            text=text,
            url=section.url,
            kind=section.kind,
            position=i,
            word_count=word_count(text),
            last_updated=section.last_updated,
        ))
    return chunks


def chunk_sections(sections: list[Section], max_words: int = 320, overlap_words: int = 40,
                   min_words: int = 20) -> list[Chunk]:
    chunks: list[Chunk] = []
    seen: set[str] = set()
    for s in sections:
        for c in chunk_section(s, max_words, overlap_words, min_words):
            if c.chunk_id in seen:          # defensive: ids must be unique for Chroma upserts
                c.chunk_id = f"{c.chunk_id}-{len(seen)}"
            seen.add(c.chunk_id)
            chunks.append(c)
    return chunks
