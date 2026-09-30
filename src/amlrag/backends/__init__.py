"""Backend factories selected by config (ollama for real runs, offline stand-ins for tests)."""
from __future__ import annotations

import logging
import re

from amlrag.backends.offline import HashEmbedder, StubLLM
from amlrag.backends.ollama import OllamaClient, OllamaEmbedder, OllamaLLM
from amlrag.config import Config

log = logging.getLogger(__name__)


def make_client(cfg: Config) -> OllamaClient:
    o = cfg.ollama
    return OllamaClient(o.host, o.timeout_s, o.keep_alive)


def embedding_prefixes(cfg: Config) -> tuple[str, str]:
    """(document prefix, query prefix) for the configured embedding model.

    Explicit embedding.document_prefix / query_prefix win; otherwise the prompt_formats entry
    whose key matches the model name (full tag, then the part before ":") is used.
    """
    e = cfg.embedding
    formats = e.get("prompt_formats", {})
    formats = formats.to_dict() if hasattr(formats, "to_dict") else dict(formats or {})
    model = str(e.model)
    fmt = formats.get(model) or formats.get(model.split(":")[0]) or {}
    doc = e.get("document_prefix", None)
    query = e.get("query_prefix", None)
    if not fmt and doc is None and query is None:
        log.warning("no prompt format configured for embedding model %s; embedding without prefixes", model)
    return (fmt.get("document", "") if doc is None else doc), (fmt.get("query", "") if query is None else query)


def make_embedder(cfg: Config):
    e = cfg.embedding
    if e.backend == "hash":
        return HashEmbedder()
    doc, query = embedding_prefixes(cfg)
    return OllamaEmbedder(make_client(cfg), e.model, doc, query, e.get("batch_size", 16))


def index_dir(cfg: Config):
    """Each embedding model gets its own index folder, so switching models never mixes vectors."""
    e = cfg.embedding
    name = "hash-512" if e.backend == "hash" else str(e.model)
    return cfg.path("chroma_dir") / re.sub(r"[^A-Za-z0-9.]+", "-", name).strip("-")


def make_llm(cfg: Config, model: str | None = None):
    g = cfg.generation
    if g.backend == "stub":
        return StubLLM()
    return OllamaLLM(make_client(cfg), model or g.model, g.temperature, g.seed, g.num_ctx, g.num_predict,
                     g.get("think", False))


def make_judge(cfg: Config):
    ev = cfg.eval
    if ev.judge_backend == "lexical" or cfg.generation.backend == "stub":
        return None
    g = cfg.generation
    return OllamaLLM(make_client(cfg), ev.judge_model, 0.0, g.seed, g.num_ctx, 256, ev.get("judge_think", False))
