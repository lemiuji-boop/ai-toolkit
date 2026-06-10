import time

from fastapi.testclient import TestClient

from app.main import app
from app.services.llm.registry import set_providers_fn

client = TestClient(app)


def _wait_job(job_id: str, timeout: float = 5.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f"/api/jobs/{job_id}")
        assert r.status_code == 200
        body = r.json()
        if body["status"] in ("done", "error"):
            return body
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} not finished in {timeout}s")


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_job_async_with_mock_provider():
    files = {"drawing": ("d.png", b"\x89PNG\r\n", "image/png")}
    r = client.post("/api/jobs", files=files)
    assert r.status_code == 202
    job_id = r.json()["job_id"]
    body = _wait_job(job_id)
    assert body["status"] == "done"
    result = body["result"]
    assert result["mode"] == "drawing_only"
    assert result["data_completeness"]["has_drawing"] is True
    assert result["extract"]["source"] == "llm"
    assert result["rows"] and result["rows"][0]["norm_per_part_kg"] is not None


def test_job_returns_503_when_no_local_provider():
    set_providers_fn(lambda: [])
    files = {"drawing": ("d.png", b"\x89PNG\r\n", "image/png")}
    r = client.post("/api/jobs", files=files)
    assert r.status_code == 202
    body = _wait_job(r.json()["job_id"])
    assert body["status"] == "error"
    assert body["error_code"] == "NO_LOCAL_PROVIDER"


def test_job_debug_returns_zones():
    files = {"drawing": ("d.png", b"\x89PNG\r\n", "image/png")}
    r = client.post("/api/jobs?debug=true", files=files)
    assert r.status_code == 202
    body = _wait_job(r.json()["job_id"])
    debug = body["result"]["debug"]
    assert debug is not None and "title_block" in debug["zones"]
