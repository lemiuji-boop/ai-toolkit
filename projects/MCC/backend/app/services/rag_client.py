"""HTTP-клиент к RAG-сервису нормативов (СЕРВИС-05, порт 8020).

Прокси в backend — удобство для Excel/орchestrator; расчёт норм остаётся в calc.py.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class RagUnavailableError(Exception):
    """RAG-сервис недоступен — вызывающий код может деградировать к stub."""


async def search(query: str, top_k: int = 5) -> dict[str, Any]:
    """POST /search на RAG. При ошибке — RagUnavailableError."""
    url = f"{settings.rag_url.rstrip('/')}/search"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json={"query": query, "top_k": top_k})
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        logger.warning("RAG search failed: %s", type(exc).__name__)
        raise RagUnavailableError(str(exc)) from exc


async def health() -> dict[str, Any]:
    """GET /health RAG."""
    url = f"{settings.rag_url.rstrip('/')}/health"
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
