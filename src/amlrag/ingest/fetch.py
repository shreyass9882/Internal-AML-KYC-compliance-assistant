"""Version-locked snapshot fetcher for the knowledge-base sources.

Run on a machine with internet access (AUSTRAC and the Federal Register of
Legislation). Every download is recorded in kb/snapshot.lock.json with its
sha256 so the evaluation can state exactly which text it was run against.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
import urllib.robotparser
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urldefrag, urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup

from amlrag.config import Config
from amlrag.textutil import slugify

log = logging.getLogger(__name__)


@dataclass
class SourceDoc:
    id: str
    title: str
    kind: str
    url: str | None
    short: str = ""
    section_label: str = "s"
    section_pattern: str | None = None
    include_parts: list[str] | None = None
    optional: bool = False
    discovered: bool = False

    @classmethod
    def from_manifest(cls, d: dict[str, Any]) -> "SourceDoc":
        return cls(
            id=d["id"],
            title=d["title"],
            kind=d.get("kind", "guidance"),
            url=d.get("url"),
            short=d.get("short") or d["title"],
            section_label=d.get("section_label", "s"),
            section_pattern=d.get("section_pattern"),
            include_parts=[str(p) for p in d.get("include_parts", [])] or None,
            optional=bool(d.get("optional", False)),
            discovered=bool(d.get("discovered", False)),
        )


def load_manifest(cfg: Config) -> tuple[list[SourceDoc], dict[str, Any]]:
    with open(cfg.path("sources_manifest"), encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    docs = [SourceDoc.from_manifest(d) for d in manifest.get("documents", [])]
    return docs, manifest


def load_lock(cfg: Config) -> dict[str, Any]:
    path = cfg.path("lock_file")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"snapshot_created": None, "documents": {}}


def all_docs(cfg: Config) -> list[SourceDoc]:
    """Manifest documents plus any pages discovered by the crawler (from the lock file)."""
    docs, _ = load_manifest(cfg)
    known = {d.id for d in docs}
    lock = load_lock(cfg)
    for doc_id, entry in lock.get("documents", {}).items():
        if doc_id not in known and entry.get("discovered"):
            docs.append(SourceDoc(id=doc_id, title=entry.get("title") or doc_id, kind="guidance",
                                  url=entry.get("url"), discovered=True))
    return docs


def raw_path_for(cfg: Config, doc: SourceDoc) -> Path | None:
    """Manual override first, then the fetched snapshot."""
    for ext in (".pdf", ".html", ".htm", ".txt"):
        manual = cfg.path("manual_dir") / f"{doc.id}{ext}"
        if manual.exists():
            return manual
    lock = load_lock(cfg)
    entry = lock.get("documents", {}).get(doc.id)
    if entry and entry.get("file"):
        p = cfg.root / entry["file"]
        if p.exists():
            return p
    return None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Fetcher:
    def __init__(self, user_agent: str, delay_s: float = 1.5, timeout_s: float = 45):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent
        self.delay_s = delay_s
        self.timeout_s = timeout_s
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self._last = 0.0

    def allowed(self, url: str) -> bool:
        host = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        if host not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                resp = self.session.get(host + "/robots.txt", timeout=self.timeout_s)
                rp.parse(resp.text.splitlines() if resp.ok else [])
                self._robots[host] = rp
            except requests.RequestException:
                self._robots[host] = None       # robots unreachable: proceed politely
        rp = self._robots[host]
        return True if rp is None else rp.can_fetch(self.session.headers["User-Agent"], url)

    def get(self, url: str) -> requests.Response:
        wait = self.delay_s - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()
        resp = self.session.get(url, timeout=self.timeout_s, allow_redirects=True)
        resp.raise_for_status()
        return resp


def _ext_for(resp: requests.Response, url: str) -> str:
    ctype = resp.headers.get("Content-Type", "").lower()
    if "pdf" in ctype or url.lower().endswith("/pdf") or url.lower().endswith(".pdf"):
        return ".pdf"
    return ".html"


def _page_title(html: bytes) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(" ", strip=True)
    if soup.title:
        return soup.title.get_text(strip=True).split("|")[0].strip()
    return None


def _links(html: bytes, base: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.find_all("a", href=True):
        url, _ = urldefrag(urljoin(base, a["href"]))
        out.append(url.rstrip("/"))
    return out


def fetch_snapshot(cfg: Config, refresh: bool = False, only: list[str] | None = None) -> dict[str, Any]:
    """Download sources not yet in the lock (or all, with refresh=True).

    Returns a report dict: fetched / skipped / changed / failed.
    """
    docs, manifest = load_manifest(cfg)
    defaults = manifest.get("defaults", {})
    fetcher = Fetcher(defaults.get("user_agent", "amlrag/0.1"), defaults.get("delay_s", 1.5),
                      defaults.get("timeout_s", 45))
    lock = load_lock(cfg)
    entries: dict[str, Any] = lock.setdefault("documents", {})
    raw_dir = cfg.path("raw_dir")
    raw_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, list[str]] = {"fetched": [], "skipped": [], "changed": [], "failed": [], "manual": []}

    def save(doc_id: str, url: str, title: str | None, discovered: bool) -> bytes | None:
        manual = next((cfg.path("manual_dir") / f"{doc_id}{e}" for e in (".pdf", ".html", ".htm", ".txt")
                       if (cfg.path("manual_dir") / f"{doc_id}{e}").exists()), None)
        if manual is not None:
            data = manual.read_bytes()
            entries[doc_id] = {**entries.get(doc_id, {}), "url": url, "file": str(manual.relative_to(cfg.root)),
                               "sha256": _sha256(data), "bytes": len(data), "source": "manual",
                               "fetched_at": datetime.fromtimestamp(manual.stat().st_mtime, timezone.utc).isoformat(),
                               "title": title, "discovered": discovered}
            report["manual"].append(doc_id)
            return data if manual.suffix in (".html", ".htm") else None
        if not url:
            return None
        if doc_id in entries and not refresh and (cfg.root / entries[doc_id].get("file", "")).exists():
            report["skipped"].append(doc_id)
            p = cfg.root / entries[doc_id]["file"]
            return p.read_bytes() if p.suffix == ".html" else None
        if not fetcher.allowed(url):
            log.warning("robots.txt disallows %s", url)
            report["failed"].append(f"{doc_id} (robots.txt)")
            return None
        try:
            resp = fetcher.get(url)
        except requests.RequestException as exc:
            log.warning("fetch failed for %s: %s", url, exc)
            report["failed"].append(f"{doc_id} ({exc.__class__.__name__})")
            return None
        data = resp.content
        ext = _ext_for(resp, url)
        path = raw_dir / f"{doc_id}{ext}"
        digest = _sha256(data)
        old = entries.get(doc_id, {}).get("sha256")
        if old and old != digest:
            report["changed"].append(doc_id)
        path.write_bytes(data)
        entries[doc_id] = {
            "url": url, "final_url": resp.url, "file": str(path.relative_to(cfg.root)),
            "sha256": digest, "bytes": len(data), "content_type": resp.headers.get("Content-Type"),
            "fetched_at": datetime.now(timezone.utc).isoformat(), "source": "web",
            "title": title or (_page_title(data) if ext == ".html" else None), "discovered": discovered,
        }
        report["fetched"].append(doc_id)
        return data if ext == ".html" else None

    for doc in docs:
        if only and doc.id not in only:
            continue
        save(doc.id, doc.url, doc.title, discovered=False)
        if doc.url is None and doc.id not in entries and not doc.optional:
            report["failed"].append(f"{doc.id} (no url; place file in kb/manual/)")

    crawl = manifest.get("crawl") or {}
    if crawl.get("enabled") and not only:
        allow = [p.rstrip("/") for p in crawl.get("allow_prefixes", [])]
        deny = crawl.get("deny_substrings", [])
        queue = deque((s.rstrip("/"), 0) for s in crawl.get("seeds", []))
        seen: set[str] = set()
        pages = 0
        while queue and pages < crawl.get("max_pages", 50):
            url, depth = queue.popleft()
            if url in seen:
                continue
            seen.add(url)
            doc_id = next((d.id for d in docs if d.url and d.url.rstrip("/") == url), None)
            html = None
            if doc_id is None:
                doc_id = "austrac-" + slugify(urlparse(url).path.rstrip("/").split("/")[-1], 70)
                existing = next((k for k, e in entries.items() if e.get("url", "").rstrip("/") == url), None)
                doc_id = existing or doc_id
                html = save(doc_id, url, None, discovered=True)
                pages += 1
            else:
                p = cfg.root / entries.get(doc_id, {}).get("file", "")
                html = p.read_bytes() if p.is_file() and p.suffix == ".html" else None
            if html is None or depth >= crawl.get("max_depth", 2):
                continue
            for link in _links(html, url):
                if any(s in link for s in deny) or not any(link.startswith(a) for a in allow):
                    continue
                if link not in seen:
                    queue.append((link, depth + 1))

    lock["snapshot_created"] = lock.get("snapshot_created") or datetime.now(timezone.utc).isoformat()
    lock["last_fetch"] = datetime.now(timezone.utc).isoformat()
    cfg.path("lock_file").write_text(json.dumps(lock, indent=2, sort_keys=True), encoding="utf-8")
    return report


def snapshot_date(cfg: Config) -> str | None:
    lock = load_lock(cfg)
    created = lock.get("snapshot_created")
    return created[:10] if created else None
