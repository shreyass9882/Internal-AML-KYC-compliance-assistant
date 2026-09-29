"""Configuration loading: YAML file + environment-variable overrides."""
from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml

ENV_PREFIX = "AMLRAG_"


class Config:
    """Thin wrapper over a nested dict with attribute access and path resolution.

    >>> cfg = Config({"retrieval": {"final_k": 8}})
    >>> cfg.retrieval.final_k
    8
    """

    def __init__(self, data: dict[str, Any], root: Path | None = None):
        self._data = data
        self._root = root or Path.cwd()

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            value = self._data[name]
        except KeyError as exc:
            raise AttributeError(f"config has no key {name!r}") from exc
        if isinstance(value, dict):
            return Config(value, self._root)
        return value

    def get(self, name: str, default: Any = None) -> Any:
        value = self._data.get(name, default)
        return Config(value, self._root) if isinstance(value, dict) else value

    def path(self, key: str) -> Path:
        """Resolve a key under `paths:` relative to the project root."""
        p = Path(self._data["paths"][key])
        return p if p.is_absolute() else self._root / p

    @property
    def root(self) -> Path:
        return self._root

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)

    def override(self, dotted: str, value: Any) -> "Config":
        """Return a copy with one dotted key replaced (used for eval ablations)."""
        data = self.to_dict()
        node = data
        parts = dotted.split(".")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value
        return Config(data, self._root)


def _coerce(raw: str) -> Any:
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError:
        return raw


def _apply_env(data: dict[str, Any]) -> None:
    for key, raw in os.environ.items():
        if not key.startswith(ENV_PREFIX):
            continue
        parts = key[len(ENV_PREFIX):].lower().split("__")
        if len(parts) < 2:
            continue
        node = data
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = _coerce(raw)


def find_root(start: Path | None = None) -> Path:
    """Walk up from `start` to the directory holding config.yaml."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "config.yaml").exists():
            return candidate
    return here


def load_config(path: str | Path | None = None) -> Config:
    if path is None:
        path = os.environ.get("AMLRAG_CONFIG") or (find_root() / "config.yaml")
    path = Path(path).resolve()
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    _apply_env(data)
    return Config(data, root=path.parent)
