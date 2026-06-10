"""Тесты API надстройки Excel (каталог, выгрузка, SEC-002)."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _setup_exports(tmp_path, monkeypatch) -> None:
    exports = tmp_path / "exports"
    (exports / "reports").mkdir(parents=True)
    (exports / "jobs").mkdir()
    (exports / "report_summary.json").write_text('{"stats":{}}', encoding="utf-8")
    (exports / "reports" / "material_norms.csv").write_text("a,b\n1,2", encoding="utf-8")
    job_payload = {
        "job_id": "test-uuid",
        "mode": "drawing_only",
        "verify": {"ok": True, "flags": []},
        "extract": {"designation": "СЕКРЕТ", "name": "Деталь", "source": "stub"},
        "geometry": {"source": "stub", "volume_cm3": 10.0},
        "rows": [
            {
                "num": 1,
                "designation": "СЕКРЕТ",
                "name": "Деталь",
                "material": "Ст3",
                "zagotovka": "лист",
                "qty_per_set": 1,
                "md_kg": 1.0,
                "mz_kg": 0.1,
                "kim": 1.1,
                "norm_per_part_kg": 1.1,
                "norm_program_kg": 1.1,
                "flags": [],
            }
        ],
    }
    (exports / "jobs" / "a1b2c3d4e5f6.json").write_text(
        json.dumps(job_payload), encoding="utf-8"
    )
    (exports / "reports" / "a1b2c3d4e5f6_summary.json").write_text(
        json.dumps({"mode": "drawing_only", "verify_ok": True, "rows_count": 1}),
        encoding="utf-8",
    )
    (exports / "reports" / "ref_8417e4e56dc9.xlsx").write_bytes(b"PK\x03\x04")
    monkeypatch.setenv("MATNORM_EXPORTS_DIR", str(exports))


def test_addin_catalog_groups(tmp_path, monkeypatch):
    _setup_exports(tmp_path, monkeypatch)
    r = client.get("/api/addin/catalog")
    assert r.status_code == 200
    body = r.json()
    assert body["job_count"] == 1
    assert body["total"] >= 4
    paths = {i["path"] for i in body["groups"]["reports"]}
    assert "report_summary.json" in paths
    assert "reports/material_norms.csv" in paths
    job = body["groups"]["jobs"][0]
    assert job["job_hash"] == "a1b2c3d4e5f6"
    assert job["mode"] == "drawing_only"
    assert job["verify_ok"] is True
    assert "designation" not in json.dumps(job)
    assert body["groups"]["reference"][0]["path"] == "reports/ref_8417e4e56dc9.xlsx"


def test_addin_fetch_job_sanitized(tmp_path, monkeypatch):
    _setup_exports(tmp_path, monkeypatch)
    r = client.post("/api/addin/fetch-job", json={"job_hash": "a1b2c3d4e5f6"})
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "drawing_only"
    assert body["verify"]["ok"] is True
    assert len(body["rows"]) == 1
    assert "designation" not in body
    assert "name" not in body["rows"][0]
    assert body["rows"][0]["material"] == "Ст3"


def test_addin_fetch_job_not_found(tmp_path, monkeypatch):
    _setup_exports(tmp_path, monkeypatch)
    r = client.post("/api/addin/fetch-job", json={"job_hash": "000000000000"})
    assert r.status_code == 404


def test_addin_export_and_download(tmp_path, monkeypatch):
    _setup_exports(tmp_path, monkeypatch)
    exp = client.post("/api/addin/export", json={"path": "report_summary.json"})
    assert exp.status_code == 200
    assert exp.json()["ok"] is True
    dl = client.get("/api/addin/download?path=report_summary.json")
    assert dl.status_code == 200
    assert dl.json() == {"stats": {}}
    bad = client.get("/api/addin/download?path=../secret.txt")
    assert bad.status_code == 404
