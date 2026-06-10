"""RAG-сервис нормативов (СЕРВИС-05): индексация, ingest, поиск, цитирование."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import store
from app.core import embed
from app.core.ingest import ingest_files
from app.core.schemas import (
    IndexRequest,
    IndexResponse,
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResponse,
)
from app.corpus import bootstrap_index


@asynccontextmanager
async def lifespan(_app: FastAPI):
    bootstrap_index()
    yield


app = FastAPI(title="МАТНОРМ RAG нормативов (СЕРВИС-05)", version="0.2.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "embed_backend": embed.embedding_backend_name()}


@app.get("/version")
def version() -> dict:
    return {
        "service": "matnorm-rag",
        "version": "0.2.0",
        "backend": store.backend_name(),
        "embed_backend": embed.embedding_backend_name(),
        "embed_dim": embed.embedding_dim(),
        "chunk_count": store.count(),
    }


@app.post("/index", response_model=IndexResponse)
def index(req: IndexRequest) -> IndexResponse:
    """FR-001: прямая индексация документов."""
    store.add(req.documents)
    return IndexResponse(indexed=len(req.documents), total=store.count())


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest) -> IngestResponse:
    """Пакетная загрузка из PDF/MD/JSON (rules.json, docs/, data/rag/)."""
    if req.reindex:
        store.clear()
    docs, files = ingest_files(req)
    store.add(docs)
    return IngestResponse(
        indexed=len(docs),
        total=store.count(),
        files=files,
        embed_backend=embed.embedding_backend_name(),
    )


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest) -> SearchResponse:
    """FR-002/003: семантический поиск с полем source у каждого hit."""
    hits = store.search(req.query, req.top_k)
    return SearchResponse(
        query=req.query,
        hits=hits,
        embed_backend=embed.embedding_backend_name(),
    )
