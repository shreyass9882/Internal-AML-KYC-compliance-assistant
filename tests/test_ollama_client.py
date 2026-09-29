"""Exercise the real Ollama client code against a local fake Ollama HTTP server."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from amlrag.backends.ollama import OllamaClient, OllamaEmbedder, OllamaError, OllamaLLM, parse_json_loose


class FakeOllama(BaseHTTPRequestHandler):
    requests: list = []
    embed_404 = False
    chat_replies: list = []

    def log_message(self, *a):
        pass

    def _send(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/tags":
            self._send(200, {"models": [{"name": "nomic-embed-text:latest"}, {"name": "llama3.1:8b"}]})
        elif self.path == "/api/version":
            self._send(200, {"version": "0.9.0"})
        else:
            self._send(404, {})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeOllama.requests.append((self.path, body))
        if self.path == "/api/embed":
            if FakeOllama.embed_404:
                return self._send(404, {"error": "not found"})
            return self._send(200, {"embeddings": [[float(len(t)), 1.0] for t in body["input"]]})
        if self.path == "/api/embeddings":
            return self._send(200, {"embedding": [float(len(body["prompt"])), 1.0]})
        if self.path == "/api/chat":
            content = FakeOllama.chat_replies.pop(0) if FakeOllama.chat_replies else '{"ok": true}'
            return self._send(200, {"message": {"content": content}, "prompt_eval_count": 100, "eval_count": 20})
        self._send(404, {})


@pytest.fixture()
def server():
    FakeOllama.requests = []
    FakeOllama.embed_404 = False
    FakeOllama.chat_replies = []
    httpd = HTTPServer(("127.0.0.1", 0), FakeOllama)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def test_embedder_uses_nomic_prefixes_and_batches(server):
    emb = OllamaEmbedder(OllamaClient(server), "nomic-embed-text", "search_document: ", "search_query: ", batch_size=2)
    vecs = emb.embed_documents(["a", "bb", "ccc"])
    assert len(vecs) == 3
    calls = [b for p, b in FakeOllama.requests if p == "/api/embed"]
    assert len(calls) == 2  # batch of 2 + batch of 1
    assert calls[0]["input"][0] == "search_document: a"
    emb.embed_query("q")
    assert FakeOllama.requests[-1][1]["input"] == ["search_query: q"]


def test_embedder_falls_back_to_legacy_endpoint(server):
    FakeOllama.embed_404 = True
    emb = OllamaEmbedder(OllamaClient(server), "nomic-embed-text", "d: ", "q: ")
    assert emb.embed_documents(["x", "y"]) == [[4.0, 1.0], [4.0, 1.0]]
    assert [p for p, _ in FakeOllama.requests].count("/api/embeddings") == 2


def test_chat_sends_schema_and_options(server):
    FakeOllama.chat_replies = ['{"tier": "enhanced"}']
    llm = OllamaLLM(OllamaClient(server), "llama3.1:8b", temperature=0.0, seed=7, num_ctx=8192)
    schema = {"type": "object", "properties": {"tier": {"type": "string"}}}
    out, stats = llm.chat_json([{"role": "user", "content": "hi"}], schema, task="determine")
    assert out == {"tier": "enhanced"} and stats["prompt_tokens"] == 100
    body = FakeOllama.requests[-1][1]
    assert body["format"] == schema and body["stream"] is False
    assert body["options"]["num_ctx"] == 8192 and body["options"]["seed"] == 7 and body["options"]["temperature"] == 0.0


def test_chat_retries_once_on_prose(server):
    FakeOllama.chat_replies = ["Sure! Here you go", '```json\n{"a": 1}\n```']
    out, stats = OllamaLLM(OllamaClient(server), "m").chat_json([{"role": "user", "content": "x"}])
    assert out == {"a": 1} and stats.get("retried")


def test_list_models_and_version(server):
    c = OllamaClient(server)
    assert "llama3.1:8b" in c.list_models() and c.version() == "0.9.0"


def test_connection_error_has_actionable_hint():
    c = OllamaClient("http://127.0.0.1:9", timeout_s=2)
    with pytest.raises(OllamaError, match="ollama serve"):
        OllamaLLM(c, "llama3.1:8b").chat_json([{"role": "user", "content": "x"}])


def test_parse_json_loose():
    assert parse_json_loose('noise {"a": {"b": 2}} trailing') == {"a": {"b": 2}}
    with pytest.raises(ValueError):
        parse_json_loose("no json at all")
