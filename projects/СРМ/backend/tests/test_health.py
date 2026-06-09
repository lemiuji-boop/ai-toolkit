from fastapi.testclient import TestClient

from app.main import app
from app.services import vision

client = TestClient(app)


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_job_runs_without_model_or_llm(monkeypatch):
    # Каркас должен отработать даже без 3D и без доступного LLM (заглушки).
    # Inference имитируем недоступным, чтобы тест был герметичным (без GPU/сети).
    def _boom(*a, **k):
        raise RuntimeError("inference unavailable")

    monkeypatch.setattr(vision.httpx, "post", _boom)
    files = {"drawing": ("d.png", b"\x89PNG\r\n", "image/png")}
    r = client.post("/api/jobs", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["extract"]["source"] == "stub"
    assert body["rows"] and body["rows"][0]["norm_per_part_kg"] is not None


def test_job_debug_returns_zones(monkeypatch):
    # FR-002: debug-режим возвращает координаты зон OCR-препроцессора.
    monkeypatch.setattr(
        vision.httpx, "post", lambda *a, **k: (_ for _ in ()).throw(RuntimeError())
    )
    files = {"drawing": ("d.png", b"\x89PNG\r\n", "image/png")}
    r = client.post("/api/jobs?debug=true", files=files)
    assert r.status_code == 200
    debug = r.json()["debug"]
    assert debug is not None and "title_block" in debug["zones"]
