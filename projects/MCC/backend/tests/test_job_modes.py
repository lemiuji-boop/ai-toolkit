"""Тесты гибкой загрузки данных: режимы drawing_only / model_only / paired."""
import pathlib
import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_DATA = pathlib.Path(__file__).resolve().parents[2] / "data"
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x08\x00\x00\x00\x08\x08\x02"
    b"\x00\x00\x00K=\xf8\x9d\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x01\x01\x01\x00"
    b"\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
STEP = (_DATA / "part.step").read_bytes()


def _wait_job(job_id: str) -> dict:
    for _ in range(100):
        r = client.get(f"/api/jobs/{job_id}")
        body = r.json()
        if body["status"] in ("done", "error"):
            return body
        time.sleep(0.05)
    raise AssertionError("timeout")


def test_drawing_only():
    files = {"drawing": ("d.png", PNG, "image/png")}
    r = client.post("/api/jobs?mode=auto", files=files)
    assert r.status_code == 202
    body = _wait_job(r.json()["job_id"])
    assert body["status"] == "done"
    result = body["result"]
    assert result["mode"] == "drawing_only"
    dc = result["data_completeness"]
    assert dc["has_drawing"] is True and dc["has_model3d"] is False
    assert dc["vision_available"] is True
    assert dc["geometry_available"] is False
    assert result["extract"]["source"] == "llm"
    assert result["geometry"]["source"] == "none"
    assert result["rows"]
    flags = result["verify"]["flags"]
    assert any("INFO:" in f for f in flags)
    assert not any("≠" in f for f in flags)


def test_model_only():
    files = {"model3d": ("part.step", STEP, "application/octet-stream")}
    r = client.post("/api/jobs?mode=auto", files=files)
    assert r.status_code == 202
    body = _wait_job(r.json()["job_id"])
    if body["status"] == "error" and body["error_code"] == "GEOMETRY_UNAVAILABLE":
        return  # cadquery не установлен в среде CI — допустимо по TZ-FINAL §3
    assert body["status"] == "done"
    result = body["result"]
    assert result["mode"] == "model_only"
    dc = result["data_completeness"]
    assert dc["has_drawing"] is False and dc["has_model3d"] is True
    assert result["extract"]["source"] == "none"
    assert result["extract"]["designation"] is None
    assert result["geometry"]["source"] in ("cad", "none")
    assert result["rows"]


def test_paired():
    files = {
        "drawing": ("d.png", PNG, "image/png"),
        "model3d": ("part.step", STEP, "application/octet-stream"),
    }
    r = client.post("/api/jobs?mode=paired", files=files)
    assert r.status_code == 202
    body = _wait_job(r.json()["job_id"])
    if body["status"] == "error":
        assert body["error_code"] in ("GEOMETRY_UNAVAILABLE", "NO_LOCAL_PROVIDER")
        return
    result = body["result"]
    assert result["mode"] == "paired"
    dc = result["data_completeness"]
    assert dc["has_drawing"] is True and dc["has_model3d"] is True
    assert result["extract"]["source"] == "llm"
    assert "verify" in result


def test_neither_422():
    r = client.post("/api/jobs")
    assert r.status_code == 422
