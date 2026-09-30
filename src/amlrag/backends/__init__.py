"""Backend factories selected by config (ollama for real runs, offline stand-ins for tests)."""
from __future__ import annotations

from amlrag.backends.offline import HashEmbedder, StubLLM
from amlrag.backends.ollama import OllamaClient, OllamaEmbedder, OllamaLLM
from amlrag.config import Config


def make_client(cfg: Config) -> OllamaClient:
    o = cfg.ollama
    return OllamaClient(o.host, o.timeout_s, o.keep_alive)


def make_embedder(cfg: Config):
    e = cfg.embedding
    if e.backend == "hash":
        return HashEmbedder()
    return OllamaEmbedder(make_client(cfg), e.model, e.document_prefix, e.query_prefix, e.batch_size)


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
