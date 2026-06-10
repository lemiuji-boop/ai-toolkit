"""Хранилище нормативов для RAG (СЕРВИС-05).

ChromaDB persistent at data/rag/chroma/. Эмбеддинги — локальный Ollama или stub.
"""
from __future__ import annotations

import logging
from typing import Any

from app.core import embed
from app.core.config import settings
from app.core.schemas import Document, Hit

logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


class _MemoryBackend:
    """Резервное in-memory хранилище с косинусным ранжированием."""

    def __init__(self) -> None:
        self._docs: dict[str, dict] = {}

    def add(self, docs: list[Document]) -> None:
        emb = embed.get_embedder()
        for d in docs:
            self._docs[d.id] = {
                "text": d.text,
                "source": d.source,
                "vec": emb.embed(d.text),
            }

    def clear(self) -> None:
        self._docs.clear()

    def count(self) -> int:
        return len(self._docs)

    def search(self, query: str, top_k: int) -> list[Hit]:
        emb = embed.get_embedder()
        qv = emb.embed(query)
        scored = [
            Hit(
                id=i,
                text=d["text"],
                source=d["source"],
                score=round(embed.cosine(qv, d["vec"]), 4),
            )
            for i, d in self._docs.items()
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:top_k]


class _ChromaBackend:
    """Бэкенд ChromaDB. Эмбеддинги передаются явно."""

    def __init__(self) -> None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        cfg = ChromaSettings(anonymized_telemetry=False)
        path = settings.resolved_chroma_path()
        self._client = chromadb.PersistentClient(path=path, settings=cfg)
        self._col: Any = self._client.get_or_create_collection(
            name=settings.collection,
            metadata={"hnsw:space": "cosine", "embed_backend": embed.embedding_backend_name()},
        )

    def add(self, docs: list[Document]) -> None:
        emb = embed.get_embedder()
        self._col.add(
            ids=[d.id for d in docs],
            documents=[d.text for d in docs],
            embeddings=[emb.embed(d.text) for d in docs],
            metadatas=[{"source": d.source} for d in docs],
        )

    def clear(self) -> None:
        self._client.delete_collection(settings.collection)
        self._col = self._client.get_or_create_collection(
            name=settings.collection,
            metadata={"hnsw:space": "cosine", "embed_backend": embed.embedding_backend_name()},
        )

    def count(self) -> int:
        return self._col.count()

    def search(self, query: str, top_k: int) -> list[Hit]:
        emb = embed.get_embedder()
        qv = emb.embed(query)
        res: Any = self._col.query(query_embeddings=[qv], n_results=top_k)
        hits: list[Hit] = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for i, doc, meta, dist in zip(ids, docs, metas, dists, strict=False):
            hits.append(
                Hit(
                    id=i,
                    text=doc,
                    source=(meta or {}).get("source", ""),
                    score=round(1.0 - float(dist), 4),
                )
            )
        return hits


def _make_backend():
    if settings.chroma_path == "memory":
        return _MemoryBackend()
    path = settings.chroma_path or settings.resolved_chroma_path()
    try:
        settings.chroma_path = path
        return _ChromaBackend()
    except Exception as exc:
        logger.warning("ChromaDB недоступен (%s), in-memory", type(exc).__name__)
        return _MemoryBackend()


_backend: _MemoryBackend | _ChromaBackend | None = None


def _get_backend() -> _MemoryBackend | _ChromaBackend:
    global _backend
    if _backend is None:
        _backend = _make_backend()
    return _backend


def reset_backend() -> None:
    """Сброс бэкенда (тесты)."""
    global _backend
    _backend = None


def backend_name() -> str:
    return type(_get_backend()).__name__.lstrip("_")


def add(docs: list[Document]) -> None:
    if docs:
        _get_backend().add(docs)


def clear() -> None:
    _get_backend().clear()


def count() -> int:
    return _get_backend().count()


def search(query: str, top_k: int | None = None) -> list[Hit]:
    return _get_backend().search(query, top_k or settings.top_k)
