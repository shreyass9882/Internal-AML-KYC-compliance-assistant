"""Ollama REST client for embeddings (nomic-embed-text) and chat (qwen3.5:9b by default)."""
from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

import requests

log = logging.getLogger(__name__)


class OllamaError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, body: str = ""):
        super().__init__(message)
        self.status = status
        self.body = body


def _hint(host: str, model: str | None = None) -> str:
    msg = f"Is Ollama running at {host}? Start it with `ollama serve`."
    if model:
        msg += f" Then make sure the model is pulled: `ollama pull {model}`."
    return msg


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434", timeout_s: float = 240, keep_alive: str = "15m"):
        self.host = host.rstrip("/")
        self.timeout_s = timeout_s
        self.keep_alive = keep_alive
        self.session = requests.Session()

    def _post(self, path: str, payload: dict[str, Any], model: str | None = None) -> dict[str, Any]:
        try:
            resp = self.session.post(f"{self.host}{path}", json=payload, timeout=self.timeout_s)
        except requests.ConnectionError as exc:
            raise OllamaError(_hint(self.host, model)) from exc
        except requests.Timeout as exc:
            raise OllamaError(f"Ollama timed out after {self.timeout_s}s on {path}. Try a smaller model "
                              f"(generation.fallback_model) or raise ollama.timeout_s.") from exc
        if resp.status_code == 404 and model:
            raise OllamaError(f"Ollama returned 404 for {path} with model {model!r}. " + _hint(self.host, model),
                              404, resp.text[:300])
        if not resp.ok:
            raise OllamaError(f"Ollama {path} failed ({resp.status_code}): {resp.text[:300]}", resp.status_code,
                              resp.text[:300])
        return resp.json()

    def list_models(self) -> list[str]:
        try:
            resp = self.session.get(f"{self.host}/api/tags", timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise OllamaError(_hint(self.host)) from exc
        return [m["name"] for m in resp.json().get("models", [])]

    def version(self) -> str | None:
        try:
            return self.session.get(f"{self.host}/api/version", timeout=10).json().get("version")
        except (requests.RequestException, ValueError):
            return None


class OllamaEmbedder:
    """nomic-embed-text via /api/embed (batched), falling back to legacy /api/embeddings."""

    def __init__(self, client: OllamaClient, model: str, document_prefix: str = "", query_prefix: str = "",
                 batch_size: int = 32):
        self.client = client
        self.model = model
        self.document_prefix = document_prefix
        self.query_prefix = query_prefix
        self.batch_size = batch_size
        self.name = f"ollama:{model}"

    def _embed(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            try:
                data = self.client._post("/api/embed", {"model": self.model, "input": batch, "truncate": True,
                                                        "keep_alive": self.client.keep_alive}, self.model)
                out.extend(data["embeddings"])
            except OllamaError as exc:
                if "404" not in str(exc):
                    raise
                for text in batch:  # Ollama < 0.3.4
                    data = self.client._post("/api/embeddings", {"model": self.model, "prompt": text}, self.model)
                    out.append(data["embedding"])
        return out

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed([self.document_prefix + t for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._embed([self.query_prefix + text])[0]


_THINK_BLOCK = re.compile(r"<think>.*?(?:</think>|$)", re.S | re.I)


def parse_json_loose(text: str) -> dict[str, Any]:
    """Parse model output as JSON, tolerating code fences, leaked <think> reasoning and surrounding prose."""
    text = _THINK_BLOCK.sub("", text).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    depth = 0
    for i in (range(start, len(text)) if start >= 0 else []):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    break
    raise ValueError(f"model did not return valid JSON: {text[:200]!r}")


class OllamaLLM:
    """Chat completion with JSON-schema constrained output (Ollama >= 0.5 structured outputs).

    think: False turns off the reasoning phase of thinking models (Qwen 3.5, Gemma 4), which is slow
    and can spill into the JSON. None leaves the model's default. Models that can't think ignore it;
    if an Ollama version rejects the field instead, it is dropped and the request retried.
    """

    def __init__(self, client: OllamaClient, model: str, temperature: float = 0.0, seed: int = 42,
                 num_ctx: int = 8192, num_predict: int = 1024, think: bool | str | None = False):
        self.client = client
        self.model = model
        self.options = {"temperature": temperature, "seed": seed, "num_ctx": num_ctx, "num_predict": num_predict}
        self.think = think
        self._send_think = think is not None
        self.name = f"ollama:{model}"

    def _chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self._send_think:
            payload = {**payload, "think": self.think}
        try:
            return self.client._post("/api/chat", payload, self.model)
        except OllamaError as exc:
            if self._send_think and exc.status == 400 and "think" in exc.body.lower():
                log.warning("%s rejected the think setting; retrying without it", self.model)
                self._send_think = False
                payload = {k: v for k, v in payload.items() if k != "think"}
                return self.client._post("/api/chat", payload, self.model)
            raise

    def chat_json(self, messages: list[dict[str, str]], schema: dict[str, Any] | None = None,
                  task: str = "") -> tuple[dict[str, Any], dict[str, Any]]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": schema or "json",
            "options": self.options,
            "keep_alive": self.client.keep_alive,
        }
        t0 = time.perf_counter()
        data = self._chat(payload)
        latency = time.perf_counter() - t0
        content = data.get("message", {}).get("content", "")
        stats = {
            "latency_s": round(latency, 3),
            "prompt_tokens": data.get("prompt_eval_count"),
            "completion_tokens": data.get("eval_count"),
            "model": self.model,
            "task": task,
            "thinking_chars": len(data.get("message", {}).get("thinking") or ""),
        }
        if stats["thinking_chars"] and self.think is False:
            log.warning("%s produced %d characters of thinking although think=false", self.model,
                        stats["thinking_chars"])
        if stats["prompt_tokens"] and stats["prompt_tokens"] >= self.options["num_ctx"] - 16:
            log.warning("prompt filled the context window (%s tokens); sources may have been truncated",
                        stats["prompt_tokens"])
        try:
            return parse_json_loose(content), stats
        except ValueError:
            # One retry with an explicit reminder; small models occasionally emit prose.
            payload["messages"] = messages + [{"role": "assistant", "content": content},
                                              {"role": "user", "content": "Return only the JSON object."}]
            data = self._chat(payload)
            stats["retried"] = True
            return parse_json_loose(data.get("message", {}).get("content", "")), stats
