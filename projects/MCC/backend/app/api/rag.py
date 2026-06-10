"""Прокси к RAG-сервису (СЕРВИС-05).

Не входит в MUST FR основного ТЗ (docs/TZ.md §10 — отдельный контейнер).
Открытый вопрос §14: нужен ли публичный /api/rag/* в монолите или только прямой вызов :8020.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import rag_client

router = APIRouter(prefix="/api/rag", tags=["rag"])


class RagSearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)


@router.post("/search")
async def rag_search(req: RagSearchRequest) -> dict:
    try:
        return await rag_client.search(req.query, req.top_k)
    except rag_client.RagUnavailableError as exc:
        raise HTTPException(status_code=503, detail="RAG-сервис недоступен") from exc
