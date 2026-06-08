# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Smoke-тесты API синхронизации."""

from fastapi.testclient import TestClient

AUTH = {"Authorization": "Bearer dev-device-token"}


def test_health(client: TestClient) -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_operations_requires_token(client: TestClient) -> None:
    r = client.get("/api/v1/mobile/operations")
    assert r.status_code == 401


def test_operations_with_token(client: TestClient) -> None:
    r = client.get("/api/v1/mobile/operations", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_login_and_me(client: TestClient) -> None:
    bad = client.post(
        "/api/v1/mobile/auth/login",
        json={"username": "ivanov", "password": "wrong"},
    )
    assert bad.status_code == 401
    ok = client.post(
        "/api/v1/mobile/auth/login",
        json={"username": "ivanov", "password": "demo123"},
    )
    assert ok.status_code == 200
    token = ok.json()["access_token"]
    me = client.get(
        "/api/v1/mobile/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert "Иванов" in me.json()["display_name"]


def test_batch_push(client: TestClient) -> None:
    body = {
        "records": [
            {
                "client_id": "pytest-1",
                "date": "2026-06-04",
                "worker": "Тест",
                "product": "Изделие",
                "operation": "Токарная",
                "value": 2.0,
                "unit": "н/ч",
                "note": "",
            }
        ]
    }
    r = client.post("/api/v1/mobile/labor-records/batch", json=body, headers=AUTH)
    assert r.status_code == 200
    payload = r.json()
    assert payload["accepted"][0]["client_id"] == "pytest-1"
