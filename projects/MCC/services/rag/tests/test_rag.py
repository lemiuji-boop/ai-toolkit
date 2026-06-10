"""Тесты RAG-сервиса нормативов (FR-001..004) — без сети и без Ollama."""
from pathlib import Path

from fastapi.testclient import TestClient

from app import store
from app.core import embed
from app.core.chunk import chunk_text
from app.core.schemas import Document
from app.main import app

client = TestClient(app)


def test_health_and_version():
    assert client.get("/health").json()["status"] == "ok"
    v = client.get("/version").json()
    assert v["service"] == "matnorm-rag"
    assert v["backend"] == "MemoryBackend"
    assert v["embed_backend"] == "stub"


def test_search_returns_hits_with_source():
    r = client.post("/search", json={"query": "припуски на поковки", "top_k": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["hits"], "ожидались результаты поиска"
    top = body["hits"][0]
    assert top["source"]
    assert "поков" in top["text"].lower() or "7505" in top["source"]


def test_index_adds_documents():
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
    v1 = embed.embed("ГОСТ припуски поковка")
    v2 = embed.embed("ГОСТ припуски поковка")
    assert v1 == v2
    assert abs(sum(x * x for x in v1) - 1.0) < 1e-6


def test_chunk_russian_technical_text():
    text = "## ГОСТ 7505\n\nПрипуски на поковки.\n\nКИМ для листа."
    docs = chunk_text(text, source="test.md", chunk_size=50, overlap=10)
    assert docs
    assert all(d.source == "test.md" for d in docs)
    assert any("7505" in d.text for d in docs)


def test_ingest_markdown_file(tmp_path: Path):
    md = tmp_path / "sample.md"
    md.write_text("# Тест\n\nНорматив про анодирование деталей.", encoding="utf-8")
    r = client.post(
        "/ingest",
        json={"paths": [str(md)], "use_default_corpus": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["indexed"] >= 1
    assert "sample.md" in body["files"]
