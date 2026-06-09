from pydantic import BaseModel, Field


class Document(BaseModel):
    """Норматив для индексации (FR-001 RAG)."""

    id: str
    text: str
    source: str  # источник с привязкой: ГОСТ/ОСТ/ТУ, пункт, версия


class IndexRequest(BaseModel):
    documents: list[Document]


class IndexResponse(BaseModel):
    indexed: int
    total: int


class Hit(BaseModel):
    id: str
    text: str
    source: str
    score: float


class SearchRequest(BaseModel):
    query: str
    top_k: int | None = None


class SearchResponse(BaseModel):
    query: str
    hits: list[Hit] = Field(default_factory=list)
