"""Тесты гибкой загрузки данных: режимы drawing_only / model_only / paired."""
import pathlib

from fastapi.testclient import TestClient

from app.main import app
from app.services import vision

client = TestClient(app)

_DATA = pathlib.Path(__file__).resolve().parents[2] / "data"
# Минимальный валидный PNG 8×8 (как data/drawing.png).
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x08\x00\x00\x00\x08\x08\x02"
    b"\x00\x00\x00K=\xf8\x9d\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x01\x01\x01\x00"
    b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
STEP = (_DATA / "part.step").read_bytes()


def _block_llm(monkeypatch) -> None:
    """Имитация недоступного inference — тест без GPU/сети."""
    monkeypatch.setattr(
        vision.httpx, "post", lambda *a, **k: (_ for _ in ()).throw(RuntimeError())
    )


def test_drawing_only(monkeypatch):
    _block_llm(monkeypatch)
    files = {"drawing": ("d.png", PNG, "image/png")}
    r = client.post("/api/jobs?mode=auto", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "drawing_only"
    dc = body["data_completeness"]
    assert dc["has_drawing"] is True and dc["has_model3d"] is False
    assert dc["vision_stub"] is True
    assert dc["geometry_stub"] is True
    assert body["extract"]["source"] == "stub"
    assert body["geometry"]["source"] == "stub"
    assert body["rows"]
    flags = body["verify"]["flags"]
    assert any("INFO:" in f for f in flags)
    assert not any("≠" in f for f in flags)


def test_model_only(monkeypatch):
    _block_llm(monkeypatch)
    files = {"model3d": ("part.step", STEP, "application/octet-stream")}
    r = client.post("/api/jobs?mode=auto", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "model_only"
    dc = body["data_completeness"]
    assert dc["has_drawing"] is False and dc["has_model3d"] is True
    assert dc["vision_stub"] is True
    assert body["extract"]["source"] == "stub"
    assert body["extract"]["designation"] is None
    assert body["geometry"]["source"] in ("cad", "stub")
    assert body["rows"]


def test_paired(monkeypatch):
    _block_llm(monkeypatch)
    files = {
        "drawing": ("d.png", PNG, "image/png"),
        "model3d": ("part.step", STEP, "application/octet-stream"),
    }
    r = client.post("/api/jobs?mode=paired", files=files)
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "paired"
    dc = body["data_completeness"]
    assert dc["has_drawing"] is True and dc["has_model3d"] is True
    assert body["extract"]["source"] == "stub"
    assert "verify" in body


def test_neither_422():
    r = client.post("/api/jobs")
    assert r.status_code == 422
