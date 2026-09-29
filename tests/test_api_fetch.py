"""API and fetcher tests."""
import json
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pytest
import yaml
from fastapi.testclient import TestClient

from amlrag.config import load_config


@pytest.fixture(scope="module")
def client(built_cfg, tmp_path_factory):
    from amlrag.server.app import create_app

    cfg = built_cfg.override("paths.query_log", str(tmp_path_factory.mktemp("log") / "q.db"))
    return TestClient(create_app(cfg))


def test_health(client):
    h = client.get("/api/health").json()
    assert h["ok"] and h["offline_stub"] and h["chunks"] > 0


def test_determine_logs_and_feedback(client):
    r = client.post("/api/determine", json={"text": "A foreign politically exposed person opens an account."}).json()
    assert r["tier"] == "enhanced" and r["query_id"] > 0
    assert client.post("/api/feedback", json={"query_id": r["query_id"], "value": "not_helpful"}).json()["ok"]
    gaps = client.get("/api/gaps").json()
    assert gaps["summary"]["total"] >= 1
    assert any(g["id"] == r["query_id"] and g["feedback"] == "not_helpful" for g in gaps["items"])


def test_explain_and_validation(client):
    assert client.post("/api/explain", json={"text": "What KYC do we collect for individuals?"}).status_code == 200
    assert client.post("/api/determine", json={"text": ""}).status_code == 422
    assert client.post("/api/feedback", json={"query_id": 999999, "value": "helpful"}).status_code == 404


def test_ui_is_served(client):
    page = client.get("/")
    assert page.status_code == 200 and "CDD Assistant" in page.text
    assert client.get("/static/app.js").status_code == 200
    assert set(client.get("/api/examples").json()) == {"determine", "explain"}


def test_health_reports_missing_index(tmp_path):
    from amlrag.server.app import create_app

    (tmp_path / "config.yaml").write_text(yaml.safe_dump({
        "paths": {"chunks_file": "none.jsonl", "chroma_dir": "none", "query_log": "q.db", "lock_file": "l.json",
                  "sources_manifest": "s.yaml", "manual_dir": "m", "raw_dir": "r"},
        "embedding": {"backend": "hash"}, "generation": {"backend": "stub"},
        "retrieval": {"collection": "austrac_cdd"}, "ollama": {"host": "x", "timeout_s": 1, "keep_alive": "1m"},
    }))
    c = TestClient(create_app(load_config(tmp_path / "config.yaml")))
    h = c.get("/api/health").json()
    assert h["ok"] is False and h["error"]
    assert c.post("/api/determine", json={"text": "hello there"}).status_code == 503


# ------------------------------------------------------------------ fetcher against a local web server
PAGE = """<html><body><main><h1>Customer due diligence</h1>
<p>Hub page with enough text to be treated as main content for the parser, repeated for length. {pad}</p>
<a href="/cdd/child">Child page</a> <a href="/elsewhere">Out of scope</a> <a href="/cdd/file.pdf">PDF</a>
</main></body></html>"""


def test_fetch_crawl_lock_and_change_detection(tmp_path):
    site = tmp_path / "site"
    (site / "cdd").mkdir(parents=True)
    (site / "cdd" / "index.html").write_text(PAGE.format(pad="x " * 120))
    (site / "cdd" / "child").mkdir()
    (site / "cdd" / "child" / "index.html").write_text("<html><body><main><h1>Child</h1><p>" + "y " * 150 +
                                                        "</p></main></body></html>")
    handler = partial(SimpleHTTPRequestHandler, directory=str(site))
    handler.log_message = lambda *a: None
    httpd = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        proj = tmp_path / "proj"
        (proj / "kb").mkdir(parents=True)
        (proj / "kb" / "sources.yaml").write_text(yaml.safe_dump({
            "defaults": {"delay_s": 0, "timeout_s": 5},
            "documents": [{"id": "hub", "title": "Hub", "kind": "guidance", "url": f"{base}/cdd"}],
            "crawl": {"enabled": True, "seeds": [f"{base}/cdd"], "allow_prefixes": [f"{base}/cdd"],
                      "deny_substrings": [".pdf"], "max_depth": 2, "max_pages": 10},
        }))
        (proj / "config.yaml").write_text(yaml.safe_dump({"paths": {
            "sources_manifest": "kb/sources.yaml", "raw_dir": "kb/raw", "manual_dir": "kb/manual",
            "lock_file": "kb/snapshot.lock.json"}}))
        cfg = load_config(proj / "config.yaml")
        from amlrag.ingest.fetch import all_docs, fetch_snapshot

        rep = fetch_snapshot(cfg)
        assert "hub" in rep["fetched"] and "austrac-child" in rep["fetched"]
        lock = json.loads((proj / "kb" / "snapshot.lock.json").read_text())
        assert lock["documents"]["austrac-child"]["discovered"] is True
        assert len(lock["documents"]["hub"]["sha256"]) == 64
        assert {d.id for d in all_docs(cfg)} == {"hub", "austrac-child"}
        # Version lock: a second fetch reuses the snapshot.
        assert fetch_snapshot(cfg)["skipped"] == ["hub", "austrac-child"]
        # A refresh after the source changed reports it.
        (site / "cdd" / "child" / "index.html").write_text("<html><body><main><h1>Child</h1><p>changed " +
                                                            "z " * 150 + "</p></main></body></html>")
        assert fetch_snapshot(cfg, refresh=True)["changed"] == ["austrac-child"]
    finally:
        httpd.shutdown()
