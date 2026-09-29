"""Parse legislation (AML/CTF Rules 2025, AML/CTF Act) into section-level units.

Works on PDF text from the Federal Register of Legislation or a plain-text
export. Citations then point at the exact rule, e.g. "AML/CTF Rules 2025, s 6-23".
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from amlrag.models import Section
from amlrag.textutil import normalise

_PART_RE = re.compile(r"^Part\s+(\d{1,2}[A-Z]?)\s*[—–\-]+\s*(.+)$")
_DIV_RE = re.compile(r"^Division\s+(\d{1,2}[A-Z]?)\s*[—–\-]+\s*(.+)$")
_TOC_TAIL_RE = re.compile(r"(\.{2,}|\s)\s*\d{1,4}\s*$")
_PAGE_NUM_RE = re.compile(r"^\s*(page\s+)?\d{1,4}\s*$", re.I)
_NEW_PARA_RE = re.compile(r"^(\(\d+[A-Z]?\)|\([a-z]{1,4}\)|\([ivx]+\)|Note(\s+\d+)?:|Example(s)?(\s+\d+)?:|Note\b|Example\b|Table\b|Item\b)")


def pdf_to_pages(path: Path) -> list[str]:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return [(page.extract_text() or "") for page in reader.pages]


# Per-page headers/footers in Federal Register compilations change from page to
# page ("Customer due diligence  Part 6", "Section 6-23"), so the repetition
# test misses them. These shapes are only dropped near the top or bottom of a page.
_EDGE_NOISE = re.compile(
    r"^(Section|Rule|Clause)\s+\d+(-\d+)?[A-Z]?$"
    r"|^(Part|Division|Subdivision)\s+\d+[A-Z]?$"
    r"|^.{3,90}\s(Part|Division|Subdivision)\s+\d+[A-Z]?$"
    r"|^(Part|Division|Subdivision)\s+\d+[A-Z]?\s+[A-Z][^\u2014\u2013]{2,90}$"
    r"|Compilation (No\.|date)|Registered:|Authorised Version",
)
_EDGE_TOP, _EDGE_BOTTOM = 5, 3


def _strip_running_heads(pages: list[str]) -> list[str]:
    """Remove header/footer lines repeated on many pages (compilation banners, page numbers)."""
    def norm(line: str) -> str:
        return re.sub(r"\d+", "#", line.strip())

    counts: Counter[str] = Counter()
    for page in pages:
        for line in set(norm(l) for l in page.splitlines() if l.strip()):
            counts[line] += 1
    threshold = max(3, int(0.3 * len(pages)))
    repeated = {l for l, c in counts.items() if c >= threshold and len(l) < 160}
    lines: list[str] = []
    for page in pages:
        page_lines = [l.strip() for l in page.splitlines() if l.strip()]
        for i, s in enumerate(page_lines):
            if _PAGE_NUM_RE.match(s) or norm(s) in repeated:
                continue
            at_edge = i < _EDGE_TOP or i >= len(page_lines) - _EDGE_BOTTOM
            if at_edge and _EDGE_NOISE.search(s):
                continue
            lines.append(_clean_line(s))
    return lines


@dataclass
class _Heading:
    idx: int
    kind: str          # part | division | section
    number: str
    title: str


def _section_sort_key(number: str) -> tuple:
    parts = re.findall(r"\d+|[A-Z]+", number)
    return tuple(int(p) if p.isdigit() else p for p in parts)


def _join_body(lines: list[str]) -> str:
    """Re-flow PDF lines into paragraphs, keeping subsection/paragraph breaks."""
    out: list[str] = []
    for line in lines:
        if not out:
            out.append(line)
            continue
        prev = out[-1].rstrip()
        new_para = bool(_NEW_PARA_RE.match(line)) or (prev.endswith((".", ":", ";")) and line[:1].isupper())
        if new_para:
            out.append(line)
        else:
            out[-1] = prev + " " + line
    text = "\n".join(out)
    text = re.sub(r"(\w)- (\w)", r"\1-\2", text)  # re-join words hyphenated across lines
    return normalise(text)


def _clean_line(line: str) -> str:
    # PDF extraction often yields en dashes / non-breaking hyphens in "6-23".
    return re.sub(r"(\d)[\u2010-\u2013](\d)", r"\1-\2", line.strip())


def parse_legislation_lines(
    lines: list[str],
    doc_id: str,
    doc_title: str,
    doc_short: str,
    section_pattern: str,
    section_label: str = "s",
    include_parts: list[str] | None = None,
    url: str | None = None,
) -> list[Section]:
    sec_re = re.compile(section_pattern)
    heads: list[_Heading] = []
    for i, line in enumerate(lines):
        if m := _PART_RE.match(line):
            heads.append(_Heading(i, "part", m.group(1), m.group(2).strip()))
        elif m := _DIV_RE.match(line):
            heads.append(_Heading(i, "division", m.group(1), m.group(2).strip()))
        elif m := sec_re.match(line):
            heads.append(_Heading(i, "section", m.group(1), m.group(2).strip()))

    # 1) Drop table-of-contents entries: trailing page numbers, or no body before the next heading.
    kept: list[_Heading] = []
    for j, h in enumerate(heads):
        nxt = heads[j + 1].idx if j + 1 < len(heads) else len(lines)
        body_len = sum(len(l) for l in lines[h.idx + 1:nxt])
        if _TOC_TAIL_RE.search(h.title) and body_len < 60:
            continue
        if h.kind == "section" and body_len < 40:
            continue
        kept.append(h)

    # 2) Section numbers must increase through the body; out-of-order matches are
    #    wrapped lines that happen to start with a number, so fold them back in.
    heads2: list[_Heading] = []
    last_key: tuple | None = None
    for h in kept:
        if h.kind == "section":
            key = _section_sort_key(h.number)
            if last_key is not None and key <= last_key:
                continue
            last_key = key
        heads2.append(h)

    sections: list[Section] = []
    part: tuple[str, str] | None = None
    division: tuple[str, str] | None = None
    for j, h in enumerate(heads2):
        if h.kind == "part":
            part, division = (h.number, h.title), None
            continue
        if h.kind == "division":
            division = (h.number, h.title)
            continue
        nxt = heads2[j + 1].idx if j + 1 < len(heads2) else len(lines)
        body = _join_body(lines[h.idx + 1:nxt])
        part_no = part[0] if part else (h.number.split("-")[0] if "-" in h.number else None)
        if include_parts and part_no not in include_parts:
            continue
        path = []
        if part:
            path.append(f"Part {part[0]}—{part[1]}")
        if division:
            path.append(f"Division {division[0]}—{division[1]}")
        path.append(f"{section_label} {h.number} {h.title}")
        sections.append(Section(
            doc_id=doc_id,
            doc_title=doc_title,
            kind="legislation",
            section_key=h.number,
            heading_path=path,
            text=body,
            url=url,
            section_title=h.title,
            doc_short=doc_short,
            section_label=section_label,
        ))
    return sections


def parse_legislation_file(path: Path, doc_id: str, doc_title: str, doc_short: str, section_pattern: str,
                           section_label: str = "s", include_parts: list[str] | None = None,
                           url: str | None = None) -> list[Section]:
    if path.suffix.lower() == ".pdf":
        lines = _strip_running_heads(pdf_to_pages(path))
    else:
        raw = [_clean_line(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        counts = Counter(raw)
        # Plain-text exports keep running heads too; drop lines repeated 3+ times.
        lines = [l for l in raw if counts[l] < 3 or _PART_RE.match(l) or _DIV_RE.match(l)]
    return parse_legislation_lines(lines, doc_id, doc_title, doc_short, section_pattern, section_label,
                                   include_parts, url)
