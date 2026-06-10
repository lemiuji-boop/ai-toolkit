"""Тесты аутентификации (T-16): login, защита /api/admin/*, истечение токена."""
from datetime import UTC, datetime, timedelta

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from app.api.auth import require_admin
from app.core.config import settings
from app.main import app
from app.services import sessions


@pytest.fixture()
def real_auth(monkeypatch):
    """Снять conftest-обход защиты и задать тестовую env-учётку."""
    app.dependency_overrides.pop(require_admin, None)
    monkeypatch.setattr(settings, "admin_user", "admin")
    monkeypatch.setattr(settings, "admin_password", "test-password-123")
    return TestClient(app)


def test_login_ok(real_auth: TestClient):
    resp = real_auth.post(
        "/api/auth/login", json={"username": "admin", "password": "test-password-123"},
    )
    assert resp.status_code == 200
    token = resp.json()["token"]
    assert sessions.verify_token(token)["sub"] == "admin"


def test_login_wrong_password_401(real_auth: TestClient):
    resp = real_auth.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_disabled_without_password(real_auth: TestClient, monkeypatch):
    """Пустой ADMIN_PASSWORD → вход отключён (503), а не открыт."""
    monkeypatch.setattr(settings, "admin_password", "")
    resp = real_auth.post("/api/auth/login", json={"username": "admin", "password": "x"})
    assert resp.status_code == 503
    assert "AUTH_DISABLED" in resp.json()["detail"]


def test_admin_requires_token(real_auth: TestClient):
    assert real_auth.get("/api/admin/progress").status_code == 401


def test_admin_with_token_200(real_auth: TestClient):
    token = real_auth.post(
        "/api/auth/login", json={"username": "admin", "password": "test-password-123"},
    ).json()["token"]
    resp = real_auth.get("/api/admin/progress", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_admin_expired_token_401(real_auth: TestClient):
    """Истёкший JWT отклоняется (TTL — контракт T-16)."""
    past = datetime.now(UTC) - timedelta(minutes=5)
    token = pyjwt.encode(
        {"sub": "admin", "role": "admin", "exp": int(past.timestamp())},
        settings.secret_key, algorithm="HS256",
    )
    resp = real_auth.get("/api/admin/progress", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_admin_garbage_token_401(real_auth: TestClient):
    resp = real_auth.get(
        "/api/admin/progress", headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert resp.status_code == 401


def test_health_and_jobs_stay_open(real_auth: TestClient):
    """Контракт §4: /health и /api/jobs не требуют JWT (надстройка Excel)."""
    assert real_auth.get("/health").status_code == 200
    # GET несуществующего задания: 404 (не 401) — маршрут открыт.
    assert real_auth.get("/api/jobs/00000000-0000-0000-0000-000000000000").status_code == 404
