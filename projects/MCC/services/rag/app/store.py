"""Хранилище нормативов для RAG (СЕРВИС-05).

Бэкенд по умолчанию — ChromaDB (persistent или in-memory). Эмбеддинги считаются
нашим детерминированным хешированием и передаются в Chroma явно, поэтому Chroma
не загружает собственных моделей (требование on-premise). При недоступности
chromadb используется встроенное in-memory косинусное хранилище — каркас
остаётся работоспособным (как заглушки в основном бэкенде).
"""
from __future__ import annotations

import logging
from typing import Any

from app.core import embed
from app.core.config import settings
from app.core.schemas import Document, Hit

# Глушим шум телеметрии chromadb: исходящих обращений в локальном контуре нет (SEC-001).
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)


class _MemoryBackend:
    """Резервное in-memory хранилище с косинусным ранжированием."""

    def __init__(self) -> None:
        self._docs: dict[str, dict] = {}

    def add(self, docs: list[Document]) -> None:
        for d in docs:
            self._docs[d.id] = {
                "text": d.text,
                "source": d.source,
                "vec": embed.embed(d.text, settings.embed_dim),
            }

    def count(self) -> int:
        return len(self._docs)

    def search(self, query: str, top_k: int) -> list[Hit]:
        qv = embed.embed(query, settings.embed_dim)
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
    """Бэкенд ChromaDB. Эмбеддинги передаются явно — без загрузки моделей."""

    def __init__(self) -> None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        # Телеметрия отключена: локальный контур не делает исходящих обращений (SEC-001).
        cfg = ChromaSettings(anonymized_telemetry=False)
        if settings.chroma_path:
            self._client = chromadb.PersistentClient(path=settings.chroma_path, settings=cfg)
        else:
            self._client = chromadb.EphemeralClient(settings=cfg)
        # Тип коллекции chromadb намеренно Any: бэкенд опционален, типы стабов строги.
        self._col: Any = self._client.get_or_create_collection(
            name=settings.collection, metadata={"hnsw:space": "cosine"}
        )

    def add(self, docs: list[Document]) -> None:
        self._col.add(
            ids=[d.id for d in docs],
            documents=[d.text for d in docs],
            embeddings=[embed.embed(d.text, settings.embed_dim) for d in docs],
            metadatas=[{"source": d.source} for d in docs],
        )

    def count(self) -> int:
        return self._col.count()

    def search(self, query: str, top_k: int) -> list[Hit]:
        qv = embed.embed(query, settings.embed_dim)
        res: Any = self._col.query(query_embeddings=[qv], n_results=top_k)
        hits: list[Hit] = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for i, doc, meta, dist in zip(ids, docs, metas, dists, strict=False):
            # cosine distance → similarity
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
    """ChromaDB при наличии, иначе in-memory."""
    try:
        return _ChromaBackend()
    except Exception:
        return _MemoryBackend()


_backend = _make_backend()


def backend_name() -> str:
    return type(_backend).__name__.lstrip("_")


def add(docs: list[Document]) -> None:
    _backend.add(docs)


def count() -> int:
    return _backend.count()


def search(query: str, top_k: int | None = None) -> list[Hit]:
    return _backend.search(query, top_k or settings.top_k)
