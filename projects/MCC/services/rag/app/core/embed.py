"""Эмбеддинги: локальный Ollama (nomic-embed-text) с деградацией к stub.

Stub — детерминированное хеширование токенов без сети (NFR-002 / on-premise).
"""
from __future__ import annotations

import hashlib
import logging
import math
import re
from typing import Protocol

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...

    @property
    def dim(self) -> int: ...

    @property
    def name(self) -> str: ...


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class StubEmbedder:
    """Детерминированный bag-of-words по MD5 токенов — без сети и моделей."""

    def __init__(self, dim: int | None = None) -> None:
        self._dim = dim or settings.embed_dim

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return "stub"

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        for tok in _tokens(text):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            vec[h % self._dim] += 1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]


class OllamaEmbedder:
    """Эмбеддинги через локальный Ollama API (/api/embeddings)."""

    def __init__(
        self,
        url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._url = (url or settings.ollama_url).rstrip("/")
        self._model = model or settings.embed_model
        self._timeout = timeout or settings.embed_timeout
        self._dim = self._probe_dim()

    @property
    def dim(self) -> int:
        return self._dim

    @property
    def name(self) -> str:
        return f"ollama:{self._model}"

    def _probe_dim(self) -> int:
        vec = self._request("probe")
        return len(vec)

    def _request(self, text: str) -> list[float]:
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.post(
                f"{self._url}/api/embeddings",
                json={"model": self._model, "prompt": text},
            )
            resp.raise_for_status()
            data = resp.json()
        embedding = data.get("embedding")
        if not embedding:
            raise ValueError("Ollama не вернул embedding")
        return [float(x) for x in embedding]

    def embed(self, text: str) -> list[float]:
        return self._request(text)


def cosine(a: list[float], b: list[float]) -> float:
    """Косинусная близость двух нормализованных векторов."""
    return sum(x * y for x, y in zip(a, b, strict=False))


def _ollama_available() -> bool:
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(f"{settings.ollama_url.rstrip('/')}/api/tags")
            return resp.status_code == 200
    except Exception:
        return False


_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    """Singleton эмбеддера с учётом EMBED_BACKEND."""
    global _embedder
    if _embedder is not None:
        return _embedder

    mode = settings.embed_backend.lower()
    if mode == "stub":
        _embedder = StubEmbedder()
    elif mode == "ollama":
        _embedder = OllamaEmbedder()
    else:
        # auto: Ollama при доступности, иначе stub (деградация каркаса).
        if _ollama_available():
            try:
                _embedder = OllamaEmbedder()
                logger.info("Эмбеддинги: %s", _embedder.name)
            except Exception as exc:
                logger.warning("Ollama недоступен (%s), stub", type(exc).__name__)
                _embedder = StubEmbedder()
        else:
            logger.info("Ollama недоступен, эмбеддинги: stub")
            _embedder = StubEmbedder()
    return _embedder


def reset_embedder() -> None:
    """Сброс singleton (для тестов)."""
    global _embedder
    _embedder = None


def embed(text: str, dim: int | None = None) -> list[float]:
    """Совместимость со старым API: dim игнорируется для Ollama."""
    _ = dim
    return get_embedder().embed(text)


def embedding_dim() -> int:
    return get_embedder().dim


def embedding_backend_name() -> str:
    return get_embedder().name
