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

import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid(client):
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_admin_requires_auth(client):
    r = await client.get("/api/v1/admin/ping")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_admin_with_token(client):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    token = login.json()["access_token"]
    r = await client.get("/api/v1/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["status"] == "admin_ok"


@pytest.mark.asyncio
async def test_me_endpoint(client):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    token = login.json()["access_token"]
    r = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "admin@example.com"
