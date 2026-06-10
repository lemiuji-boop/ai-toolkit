"""Прокси RAG в backend (RAG-INT-001)."""
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rag_search_proxy_ok():
    mock_payload = {
        "query": "КИМ",
        "hits": [{"id": "1", "text": "тест", "source": "ГОСТ", "score": 0.9}],
        "embed_backend": "stub",
    }
    with patch("app.api.rag.rag_client.search", new_callable=AsyncMock, return_value=mock_payload):
        r = client.post("/api/rag/search", json={"query": "КИМ", "top_k": 3})
    assert r.status_code == 200
    assert r.json()["hits"][0]["source"]


def test_rag_search_proxy_unavailable():
    from app.services.rag_client import RagUnavailableError

    with patch(
        "app.api.rag.rag_client.search",
        new_callable=AsyncMock,
        side_effect=RagUnavailableError("down"),
    ):
        r = client.post("/api/rag/search", json={"query": "КИМ"})
    assert r.status_code == 503
