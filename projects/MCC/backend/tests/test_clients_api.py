"""Тесты мониторинга подключений клиентов: middleware, /api/admin/clients, персистентность."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import clients_monitor


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Клиент с изолированным снапшотом clients.jsonl и чистым состоянием."""
    monkeypatch.setenv("MATNORM_CLIENTS_PATH", str(tmp_path / "clients.jsonl"))
    clients_monitor.reset_for_tests()
    yield TestClient(app)
    clients_monitor.reset_for_tests()


def test_api_requests_are_tracked(client: TestClient):
    client.get("/api/admin/status")
    client.get("/api/admin/jobs")
    body = client.get("/api/admin/clients").json()
    assert len(body["clients"]) == 1
    rec = body["clients"][0]
    assert rec["ip"] == "testclient"
    # /api/admin/status, /api/admin/jobs и сам /api/admin/clients
    assert rec["requests"] >= 3
    assert rec["last_endpoint"] == "/api/admin/clients"
    assert rec["first_seen"] <= rec["last_seen"]
    assert "server_ips" in body and "127.0.0.1" in body["server_ips"]


def test_health_not_tracked(client: TestClient):
    """Healthcheck-и (вне /api и /addin) не засоряют журнал подключений."""
    client.get("/health")
    clients = clients_monitor.list_clients()
    assert clients == []


def test_persist_and_reload(client: TestClient, tmp_path):
    for _ in range(6):  # больше порога _FLUSH_EVERY — снапшот точно на диске
        client.get("/api/admin/jobs")
    path = tmp_path / "clients.jsonl"
    assert path.is_file()

    clients_monitor.reset_for_tests()
    assert clients_monitor.load_persisted() == 1
    rec = clients_monitor.list_clients()[0]
    assert rec["ip"] == "testclient"
    assert rec["requests"] >= 5


def test_user_agent_recorded(client: TestClient):
    client.get("/api/admin/jobs", headers={"User-Agent": "Excel/16.0 (Windows NT)"})
    rec = clients_monitor.list_clients()[0]
    assert "Excel/16.0" in (rec.get("user_agent") or "")
