"""Тесты API админ-панели (без внешней сети — моки проб)."""

from __future__ import annotations

import json
import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import admin_monitor, job_store

client = TestClient(app)


def _wait_job(job_id: str) -> dict:
    for _ in range(100):
        r = client.get(f"/api/jobs/{job_id}")
        body = r.json()
        if body["status"] in ("done", "error"):
            return body
        time.sleep(0.05)
    raise AssertionError("timeout")


async def _fake_probe_all() -> dict[str, dict]:
    return {
        "backend": {
            "ok": True,
            "latency_ms": 1.0,
            "status_code": 200,
            "launch_hint": "uvicorn",
        },
        "rag": {
            "ok": False,
            "latency_ms": 2.0,
            "error": "ConnectError",
            "source": "stub",
            "launch_hint": "rag",
        },
        "ollama": {
            "ok": True,
            "latency_ms": 3.0,
            "models": ["qwen2.5vl:3b"],
            "launch_hint": "ollama",
        },
        "addin": {
            "ok": True,
            "latency_ms": 4.0,
            "status_code": 200,
            "launch_hint": "addin",
        },
        "tunnel": {
            "ok": True,
            "latency_ms": 5.0,
            "url": "https://test.trycloudflare.com",
            "launch_hint": "tunnel",
        },
    }


def test_admin_status_aggregated(monkeypatch):
    monkeypatch.setattr(admin_monitor, "probe_all", _fake_probe_all)
    r = client.get("/api/admin/status")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "degraded"
    assert body["services"]["backend"]["ok"] is True
    assert "active_jobs" in body
    assert body["services"]["tunnel"]["ok"] is True


def test_admin_status_tunnel_url(monkeypatch, tmp_path):
    monkeypatch.setattr(admin_monitor, "probe_all", _fake_probe_all)
    url_file = tmp_path / ".tunnel-url"
    url_file.write_text("https://example.trycloudflare.com\n", encoding="utf-8")
    monkeypatch.setenv("MATNORM_TUNNEL_URL_FILE", str(url_file))
    r = client.get("/api/admin/status")
    assert r.status_code == 200
    assert r.json()["tunnel_url"] == "https://example.trycloudflare.com"


def test_admin_metrics_structure(monkeypatch):
    monkeypatch.setattr(
        admin_monitor,
        "collect_gpu_metrics",
        lambda: {"gpus": [], "source": "stub", "reason": "test"},
    )
    r = client.get("/api/admin/metrics")
    assert r.status_code == 200
    body = r.json()
    assert "gpu" in body
    assert "memory" in body
    assert "cpu_load" in body
    assert body["gpu"]["source"] == "stub"


def test_admin_jobs_after_pipeline():
    before = client.get("/api/admin/jobs").json()["total"]
    files = {"drawing": ("d.png", b"\x89PNG\r\n", "image/png")}
    job_resp = client.post("/api/jobs", files=files)
    assert job_resp.status_code == 202
    job_id = job_resp.json()["job_id"]
    finished = _wait_job(job_id)
    assert finished["status"] == "done"

    jobs = client.get("/api/admin/jobs").json()
    assert jobs["total"] >= before + 1
    record = jobs["jobs"][0]
    assert record["job_id"] == job_id
    assert "input_hash" in record
    assert "designation" not in record
    assert record["mode"] == "drawing_only"


def test_admin_services_includes_system(monkeypatch):
    monkeypatch.setattr(admin_monitor, "probe_all", _fake_probe_all)
    r = client.get("/api/admin/services")
    assert r.status_code == 200
    body = r.json()
    assert "services" in body
    assert body["system"]["service"] == "matnorm-backend"
    assert "rules_version" in body["system"]


def test_admin_restart_not_implemented():
    r = client.post("/api/admin/services/backend/restart")
    assert r.status_code == 501


def test_admin_restart_unknown_service():
    r = client.post("/api/admin/services/unknown/restart")
    assert r.status_code == 404


def test_admin_progress_from_summary(tmp_path, monkeypatch):
    exports = tmp_path / "exports"
    exports.mkdir()
    summary = {
        "stats": {"jobs_total": 10, "jobs_ok": 8, "jobs_failed": 1},
    }
    (exports / "report_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    monkeypatch.setenv("MATNORM_EXPORTS_DIR", str(exports))
    r = client.get("/api/admin/progress")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 10
    assert body["completed"] == 8
    assert body["failed"] == 1
    assert body["in_progress"] == 1
    assert body["source"] == "report_summary"


def test_admin_exports_list(tmp_path, monkeypatch):
    exports = tmp_path / "exports"
    (exports / "reports").mkdir(parents=True)
    (exports / "report_summary.json").write_text("{}", encoding="utf-8")
    (exports / "reports" / "material_norms.csv").write_text("a,b\n1,2", encoding="utf-8")
    (exports / "jobs").mkdir()
    (exports / "jobs" / "a1b2c3d4e5f6.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("MATNORM_EXPORTS_DIR", str(exports))
    r = client.get("/api/admin/exports")
    assert r.status_code == 200
    body = r.json()
    assert body["job_count"] == 1
    paths = {f["path"] for f in body["files"]}
    assert "report_summary.json" in paths
    assert "reports/material_norms.csv" in paths
    assert "jobs/a1b2c3d4e5f6.json" in paths


def test_admin_exports_download_and_traversal(tmp_path, monkeypatch):
    exports = tmp_path / "exports"
    exports.mkdir()
    (exports / "report_summary.json").write_text('{"ok":true}', encoding="utf-8")
    monkeypatch.setenv("MATNORM_EXPORTS_DIR", str(exports))
    ok = client.get("/api/admin/exports/download?path=report_summary.json")
    assert ok.status_code == 200
    assert ok.json() == {"ok": True}
    bad = client.get("/api/admin/exports/download?path=../secret.txt")
    assert bad.status_code == 404


def test_admin_rag_overview(monkeypatch):
    async def _fake_health():
        return {"status": "ok", "embed_backend": "test"}

    async def _fake_version():
        return {"ok": True, "version": "0.2.0", "chunk_count": 42}

    monkeypatch.setattr("app.services.rag_client.health", _fake_health)
    monkeypatch.setattr(admin_monitor, "probe_rag_version", _fake_version)
    r = client.get("/api/admin/rag/overview")
    assert r.status_code == 200
    body = r.json()
    assert body["health"]["ok"] is True
    assert body["version"]["chunk_count"] == 42
    assert "rules.json" in body["description"]


def test_job_store_persists_and_reloads(tmp_path, monkeypatch):
    """Журнал заданий сохраняется в JSONL и подгружается при старте."""
    jobs_path = tmp_path / "jobs.jsonl"
    exports_dir = tmp_path / "exports" / "jobs"
    exports_dir.mkdir(parents=True)
    monkeypatch.setenv("MATNORM_ADMIN_JOBS_PATH", str(jobs_path))
    monkeypatch.setenv("MATNORM_EXPORTS_JOBS_DIR", str(exports_dir))

    job_store.reset_for_tests()
    payload = {
        "job_id": "import-test-uuid",
        "mode": "drawing_only",
        "data_completeness": {"has_drawing": True, "has_model3d": False},
        "extract": {"source": "stub"},
        "geometry": {"source": "stub"},
        "verify": {"ok": True, "flags": []},
        "rows": [{"num": 1}],
    }
    (exports_dir / "abc123.json").write_text(json.dumps(payload), encoding="utf-8")

    loaded = job_store.load_persisted()
    assert loaded == 1
    assert jobs_path.is_file()
    records = job_store.list_jobs()
    assert records[0]["job_id"] == "import-test-uuid"
    assert records[0]["source"] == "export"
    job_store.reset_for_tests()
