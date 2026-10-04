"""Parse AUSTRAC guidance pages (Drupal HTML) into heading-scoped sections."""
from __future__ import annotations

import re
from collections import Counter
from urllib.parse import quote

from bs4 import BeautifulSoup, NavigableString, Tag

from amlrag.models import Section
from amlrag.textutil import normalise, slugify

_DROP_TAGS = ("script", "style", "noscript", "nav", "header", "footer", "aside", "form", "svg", "iframe", "template")
_DROP_SELECTORS = (
    "[role=navigation]", ".breadcrumb", ".breadcrumbs", ".visually-hidden", ".sr-only", ".skip-link",
    ".social-share", ".page-feedback", ".feedback", ".region-sidebar", ".sidebar", ".toc", ".on-this-page",
    ".related-content", ".pager", ".print-link", "#block-feedback",
)
_HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}
_TEXT_BLOCKS = {"p", "blockquote", "pre", "dt", "dd", "figcaption", "address"}
_CONTAINERS = {"div", "section", "article", "main", "ul", "ol", "dl", "span", "details", "body", "html",
               "button", "strong", "em", "b", "i", "a", "label", "figure", "fieldset"}
_BOILERPLATE_HEADINGS = re.compile(
    r"^(related (content|links|pages|guidance)|was this page helpful|feedback|share this page|"
    r"contact us|on this page|in this section|need help\??|subscribe|print|last updated|"
    r"page last updated|you may also be interested in)\b",
    re.I,
)
_UPDATED_RE = re.compile(
    r"(?:last\s+(?:updated|modified|reviewed)|page\s+updated|updated)\s*:?\s*"
    r"(\d{1,2}\s+[A-Z][a-z]+\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})",
    re.I,
)


def _main_region(soup: BeautifulSoup) -> Tag:
    for finder in (
        lambda s: s.find("main"),
        lambda s: s.find(attrs={"role": "main"}),
        lambda s: s.find("article"),
        lambda s: s.find(id=re.compile(r"^(main-)?content$")),
    ):
        node = finder(soup)
        if isinstance(node, Tag) and len(node.get_text(strip=True)) > 200:
            return node
    # Fallback: the element with the most paragraph text.
    best, best_len = soup.body or soup, 0
    for div in soup.find_all(["div", "section"]):
        n = sum(len(p.get_text(strip=True)) for p in div.find_all("p", recursive=False))
        if n > best_len:
            best, best_len = div, n
    return best


def _table_text(table: Tag) -> str:
    rows = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        if any(cells):
            rows.append(" | ".join(cells))
    return "\n".join(rows)


class _Walker:
    def __init__(self, page_title: str):
        self.page_title = page_title
        self.stack: list[tuple[int, str, str | None]] = []  # (level, text, anchor)
        self.buffer: list[str] = []
        self.sections: list[tuple[list[str], str | None, str]] = []

    def flush(self) -> None:
        text = "\n".join(t for t in self.buffer if t.strip())
        if text.strip():
            path = [h for _, h, _ in self.stack]
            anchor = next((a for _, _, a in reversed(self.stack) if a), None)
            self.sections.append((path, anchor, text))
        self.buffer = []

    def heading(self, level: int, text: str, anchor: str | None) -> None:
        self.flush()
        if level == 1:
            self.stack = []
            return  # the page title is carried separately
        while self.stack and self.stack[-1][0] >= level:
            self.stack.pop()
        self.stack.append((level, text, anchor))

    def walk(self, node: Tag, list_depth: int = 0) -> None:
        for child in node.children:
            if isinstance(child, NavigableString):
                txt = str(child).strip()
                if len(txt) > 40 and node.name in ("div", "section", "article", "main", "td"):
                    self.buffer.append(txt)
                continue
            if not isinstance(child, Tag):
                continue
            name = child.name
            if name in _HEADINGS:
                text = child.get_text(" ", strip=True)
                if text:
                    self.heading(_HEADINGS[name], text, child.get("id"))
            elif name == "summary":
                text = child.get_text(" ", strip=True)
                if text:
                    level = (self.stack[-1][0] + 1) if self.stack else 3
                    self.heading(min(level, 6), text, child.get("id"))
            elif name == "li":
                nested = [c for c in child.find_all(["ul", "ol"], recursive=False)]
                for n in nested:
                    n.extract()
                own = child.get_text(" ", strip=True)
                if own:
                    self.buffer.append("  " * list_depth + "- " + own)
                for n in nested:
                    self.walk(n, list_depth + 1)
            elif name == "table":
                self.buffer.append(_table_text(child))
            elif name in _TEXT_BLOCKS:
                if child.find(list(_HEADINGS)):
                    self.walk(child, list_depth)
                else:
                    text = child.get_text(" ", strip=True)
                    if text:
                        self.buffer.append(text)
            elif name in _CONTAINERS or name not in ("br", "hr", "img"):
                self.walk(child, list_depth + (1 if name in ("ul", "ol") and list_depth else 0))


def parse_guidance_html(html: bytes | str, doc_id: str, doc_title: str, url: str | None) -> list[Section]:
    soup = BeautifulSoup(html, "lxml")
    page_text = soup.get_text(" ", strip=True)
    m = _UPDATED_RE.search(page_text)
    last_updated = m.group(1) if m else None

    for tag in soup.find_all(_DROP_TAGS):
        tag.decompose()
    for sel in _DROP_SELECTORS:
        for tag in soup.select(sel):
            tag.decompose()

    main = _main_region(soup)
    h1 = main.find("h1") or soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else doc_title
    title = title or doc_title

    walker = _Walker(title)
    walker.walk(main)
    walker.flush()

    sections: list[Section] = []
    key_counts: Counter[str] = Counter()
    for path, anchor, text in walker.sections:
        if path and _BOILERPLATE_HEADINGS.match(path[-1]):
            continue
        if _UPDATED_RE.fullmatch(text.strip()):
            continue
        key = "--".join(slugify(p, 40) for p in path) if path else "introduction"
        key_counts[key] += 1
        if key_counts[key] > 1:
            key = f"{key}-{key_counts[key]}"
        sections.append(Section(
            doc_id=doc_id,
            doc_title=title,
            kind="guidance",
            section_key=key,
            heading_path=[title, *path],
            text=normalise(text),
            # AUSTRAC heading ids contain spaces and curly quotes ("When you don’t need to …");
            # percent-encode so the link stays one clickable URL. Browsers decode it to find the id.
            url=(f"{url}#{quote(anchor, safe='')}" if url and anchor else url),
            section_title=path[-1] if path else title,
            doc_short=f"AUSTRAC: {title}",
            last_updated=last_updated,
        ))
    return sections
