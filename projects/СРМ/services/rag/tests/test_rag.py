"""Тесты RAG-сервиса нормативов (FR-001..004) — без сети и без загрузки моделей."""
from fastapi.testclient import TestClient

from app import store
from app.core import embed
from app.core.schemas import Document
from app.main import app

client = TestClient(app)


def test_health_and_version():
    assert client.get("/health").json()["status"] == "ok"
    v = client.get("/version").json()
    assert v["service"] == "matnorm-rag"
    assert v["backend"] in {"MemoryBackend", "ChromaBackend"}


def test_search_returns_hits_with_source():
    # FR-002/003: поиск возвращает релевантные фрагменты с непустым источником.
    with TestClient(app):  # прогоняем lifespan (сид нормативов)
        r = client.post("/search", json={"query": "припуски на поковки", "top_k": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["hits"], "ожидались результаты поиска"
    top = body["hits"][0]
    assert top["source"]
    # Наиболее релевантный — норматив про поковки.
    assert "поков" in top["text"].lower() or "7505" in top["source"]


def test_index_adds_documents():
    # FR-001: индексация увеличивает объём базы и делает документ находимым.
    before = store.count()
    doc = Document(
        id="test-tu-001",
        text="Уникальный норматив про анодирование кронштейнов узлов крепления.",
        source="ТУ 1.2.3-2026, п. 5",
    )
    r = client.post("/index", json={"documents": [doc.model_dump()]})
    assert r.status_code == 200
    assert r.json()["total"] == before + 1
    found = client.post("/search", json={"query": "анодирование кронштейнов", "top_k": 1}).json()
    assert found["hits"][0]["id"] == "test-tu-001"


def test_embed_is_deterministic_and_normalized():
    v1 = embed.embed("ГОСТ припуски поковка", 256)
    v2 = embed.embed("ГОСТ припуски поковка", 256)
    assert v1 == v2
    assert abs(sum(x * x for x in v1) - 1.0) < 1e-6
