"""Shared fixtures: a tiny, fully offline project (synthetic corpus, hash embedder, stub LLM)."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from amlrag.config import load_config

FIXTURES = Path(__file__).parent / "fixtures"
REPO = Path(__file__).resolve().parents[1]


def _write_project(root: Path) -> Path:
    (root / "kb" / "manual").mkdir(parents=True)
    shutil.copy(FIXTURES / "austrac_ecdd_sample.html", root / "kb" / "manual" / "austrac-ecdd.html")
    shutil.copy(FIXTURES / "austrac_individuals_sample.html", root / "kb" / "manual" / "austrac-cdd-individuals.html")
    shutil.copy(FIXTURES / "rules_sample.txt", root / "kb" / "manual" / "rules2025.txt")
    manifest = {
        "documents": [
            {"id": "rules2025", "title": "Synthetic Rules", "short": "AML/CTF Rules 2025", "kind": "legislation",
             "url": None, "section_label": "s",
             "section_pattern": r"^(\d{1,2}-\d{1,3}[A-Z]?)\s+([A-Z][^\n]{2,160})$", "include_parts": ["1", "6"]},
            {"id": "austrac-ecdd", "title": "Enhanced customer due diligence", "kind": "guidance",
             "url": "https://example.org/ecdd"},
            {"id": "austrac-cdd-individuals", "title": "Initial CDD for individuals", "kind": "guidance",
             "url": "https://example.org/individuals"},
        ],
        "crawl": {"enabled": False},
    }
    (root / "kb" / "sources.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    cfg = yaml.safe_load((REPO / "config.yaml").read_text(encoding="utf-8"))
    cfg["embedding"]["backend"] = "hash"
    cfg["generation"]["backend"] = "stub"
    cfg["eval"]["judge_backend"] = "lexical"
    cfg["retrieval"]["min_dense_similarity"] = 0.05
    cfg["retrieval"]["final_k"] = 6
    cfg["paths"]["gold_file"] = str(FIXTURES / "gold_sample.jsonl")
    (root / "config.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return root / "config.yaml"


@pytest.fixture(scope="session")
def offline_cfg(tmp_path_factory):
    root = tmp_path_factory.mktemp("proj")
    return load_config(_write_project(root))


@pytest.fixture(scope="session")
def built_cfg(offline_cfg):
    from amlrag.backends import index_dir, make_embedder
    from amlrag.index.store import build_index
    from amlrag.ingest.build import build_chunks, read_chunks

    build_chunks(offline_cfg)
    chunks = read_chunks(offline_cfg.path("chunks_file"))
    build_index(chunks, make_embedder(offline_cfg), index_dir(offline_cfg),
                offline_cfg.retrieval.collection, "2026-01-01")
    return offline_cfg


@pytest.fixture(scope="session")
def assistant(built_cfg):
    from amlrag.pipeline import Assistant

    return Assistant.from_config(built_cfg)
