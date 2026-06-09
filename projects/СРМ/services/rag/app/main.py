"""RAG-сервис нормативов (СЕРВИС-05): индексация, поиск и цитирование источника."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import store
from app.core.schemas import (
    IndexRequest,
    IndexResponse,
    SearchRequest,
    SearchResponse,
)
from app.seed import SEED


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Первичное наполнение индекса демонстрационными нормативами (если пуст).
    if store.count() == 0:
        store.add(SEED)
    yield


app = FastAPI(title="МАТНОРМ RAG нормативов (СЕРВИС-05)", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/version")
def version() -> dict:
    return {"service": "matnorm-rag", "version": "0.1.0", "backend": store.backend_name()}


@app.post("/index", response_model=IndexResponse)
def index(req: IndexRequest) -> IndexResponse:
    store.add(req.documents)
    return IndexResponse(indexed=len(req.documents), total=store.count())


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    hits = store.search(req.query, req.top_k)
    return SearchResponse(query=req.query, hits=hits)
