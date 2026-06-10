"""Аудит: админ-эндпойнты не раскрывают имена файлов и обозначения (SEC-002)."""

from __future__ import annotations

import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import admin_monitor

client = TestClient(app)


def _wait_job(job_id: str) -> dict:
    for _ in range(100):
        r = client.get(f"/api/jobs/{job_id}")
        body = r.json()
        if body["status"] in ("done", "error"):
            return body
        time.sleep(0.05)
    raise AssertionError("timeout")

# Поля, которые не должны попадать в публичный журнал админки
_FORBIDDEN_JOB_KEYS = frozenset(
    {
        "designation",
        "name",
        "filename",
        "file_name",
        "filepath",
        "file_path",
        "drawing_name",
        "model_name",
        "source_path",
    }
)


async def _fake_probe_all() -> dict[str, dict]:
    return {
        "backend": {"ok": True, "latency_ms": 1.0},
        "rag": {"ok": False, "latency_ms": 1.0, "source": "stub"},
        "ollama": {"ok": True, "latency_ms": 1.0, "models": ["test-model"]},
        "addin": {"ok": True, "latency_ms": 1.0},
    }


def test_admin_endpoints_no_sensitive_leaks(monkeypatch):
    """Журнал /api/admin/jobs содержит только метаданные без обозначений и имён файлов."""
    monkeypatch.setattr(admin_monitor, "probe_all", _fake_probe_all)

    # Задание с «чувствительным» именем файла в multipart — не должно попасть в админку
    files = {
        "drawing": (
            "SECRET-DRAWING-BA74.pdf",
            b"\x89PNG\r\n\x1a\n",
            "application/pdf",
        ),
    }
    job_resp = client.post("/api/jobs", files=files)
    assert job_resp.status_code == 202
    job_body = _wait_job(job_resp.json()["job_id"])
    assert job_body["status"] == "done"
    # API jobs отдаёт designation (контракт FR) — это ожидаемо для вызывающего клиента
    assert job_body["result"]["extract"].get("designation") is not None

    admin_jobs = client.get("/api/admin/jobs").json()
    assert admin_jobs["jobs"], "ожидается хотя бы одна запись в журнале"
    record = admin_jobs["jobs"][0]

    for key in _FORBIDDEN_JOB_KEYS:
        assert key not in record, f"поле {key!r} не должно быть в admin jobs"

    # Значения записи — только разрешённые метаданные
    allowed = {
        "job_id",
        "input_hash",
        "mode",
        "status",
        "data_completeness",
        "vision_available",
        "geometry_available",
        "verify_ok",
        "flags_count",
        "rows_count",
        "started_at",
        "finished_at",
        "source",
    }
    assert set(record.keys()).issubset(allowed)

    # input_hash — короткий хеш, не имя файла
    assert record["input_hash"]
    assert ".pdf" not in record["input_hash"]
    assert "SECRET" not in record["input_hash"]
