"""Тесты CRUD провайдеров ИИ: маскирование ключей, пресеты, confidential-гард,
test-connection без выхода во внешнюю сеть (SEC-001)."""
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import providers_store
from app.services.llm.base import DataClass
from app.services.llm.registry import list_providers, set_providers_fn
from app.services.llm.router import choose


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Клиент с изолированным файлом хранилища провайдеров."""
    monkeypatch.setenv("MATNORM_PROVIDERS_PATH", str(tmp_path / "providers.json"))
    return TestClient(app)


def _create_external(client: TestClient, name: str = "claude-test") -> dict:
    resp = client.post("/api/admin/providers", json={
        "name": name,
        "preset": "claude",
        "model": "claude-sonnet-4",
        "api_key": "sk-ant-secret-key-12345678",
    })
    assert resp.status_code == 201
    return resp.json()


def test_create_masks_api_key(client: TestClient):
    """Ключ в ответе только маскированный; в файле — только шифртекст."""
    created = _create_external(client)
    assert created["api_key_masked"] == "••••5678"
    assert created["has_api_key"] is True
    assert "api_key" not in created
    assert "api_key_encrypted" not in created
    # На диске нет открытого ключа.
    raw = json.loads(providers_store._store_path().read_text(encoding="utf-8"))
    assert "sk-ant-secret-key-12345678" not in json.dumps(raw)


def test_preset_fills_kind_and_base_url(client: TestClient):
    created = _create_external(client)
    assert created["kind"] == "external"
    assert created["base_url"] == "https://api.anthropic.com"


def test_list_and_delete(client: TestClient):
    created = _create_external(client)
    listed = client.get("/api/admin/providers").json()
    assert [p["id"] for p in listed["providers"]] == [created["id"]]
    assert "ollama" in listed["presets"]
    assert listed["allow_external"] is False

    resp = client.delete(f"/api/admin/providers/{created['id']}")
    assert resp.status_code == 200 and resp.json()["deleted"] is True
    assert client.get("/api/admin/providers").json()["providers"] == []
    assert client.delete(f"/api/admin/providers/{created['id']}").status_code == 404


def test_duplicate_name_409(client: TestClient):
    _create_external(client, name="dup")
    resp = client.post("/api/admin/providers", json={
        "name": "dup", "preset": "openai", "model": "gpt-5", "api_key": "sk-x",
    })
    assert resp.status_code == 409


def test_external_requires_api_key(client: TestClient):
    resp = client.post("/api/admin/providers", json={
        "name": "no-key", "preset": "deepseek", "model": "deepseek-chat",
    })
    assert resp.status_code == 422


def test_local_preset_without_key(client: TestClient):
    resp = client.post("/api/admin/providers", json={
        "name": "local-ollama", "preset": "ollama", "model": "qwen3-vl:8b-instruct",
    })
    assert resp.status_code == 201
    assert resp.json()["kind"] == "local"
    assert resp.json()["has_api_key"] is False


def test_confidential_routing_ignores_external(client: TestClient):
    """FR-081/SEC-001: confidential выбирает только local, даже при внешних в базе."""
    _create_external(client, name="ext-high-prio")
    client.post("/api/admin/providers", json={
        "name": "local-1", "preset": "ollama", "model": "qwen3-vl:8b-instruct",
        "priority": 500,
    })
    set_providers_fn(None)  # снять мок conftest — реальный реестр из хранилища
    chosen = choose(DataClass.confidential, list_providers)
    assert chosen.info.kind == "local"


def test_external_excluded_without_allow_flag(client: TestClient):
    """SEC-001: без ALLOW_EXTERNAL_PROVIDERS=1 внешние не участвуют в маршрутизации."""
    _create_external(client)
    set_providers_fn(None)
    kinds = {p.info.kind for p in list_providers()}
    assert kinds == {"local"}


def test_test_connection_external_validation_only(client: TestClient):
    """test-connection внешнего провайдера не ходит в сеть (checked=validation)."""
    created = _create_external(client)
    resp = client.post(f"/api/admin/providers/{created['id']}/test")
    assert resp.status_code == 200
    body = resp.json()
    assert body["checked"] == "validation"
    assert body["ok"] is True
    assert "SEC-001" in body["detail"]


def test_test_connection_external_invalid_url(client: TestClient):
    """http:// для внешнего провайдера — ошибка валидации (без сети)."""
    resp = client.post("/api/admin/providers", json={
        "name": "bad-url", "kind": "external", "base_url": "http://insecure.example",
        "model": "m", "api_key": "sk-x",
    })
    created = resp.json()
    body = client.post(f"/api/admin/providers/{created['id']}/test").json()
    assert body["ok"] is False
    assert body["checked"] == "validation"


def test_test_connection_404(client: TestClient):
    assert client.post("/api/admin/providers/999/test").status_code == 404
