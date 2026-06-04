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

"""Интеграционные тесты API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_analyze_blocked_credentials(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/analyze",
        json={
            "project_name": "Secret",
            "task": "Deploy with api_key=sk-live-abcdefghijklmnopqrstuvwxyz123456",
            "context_lines": 0,
        },
    )
    assert resp.status_code == 422
    detail = resp.json()["detail"]
    assert "detected_violations" in detail or "credentials" in str(detail).lower()


@pytest.mark.asyncio
async def test_analyze_crud_success(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/analyze",
        json={
            "project_name": "ShopAPI",
            "task": "Создать CRUD REST API для каталога товаров с endpoints и валидацией",
            "context_lines": 100,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["complexity_level"] in ("L1", "L2", "L3", "L4")
    assert "final_markdown" in data
    assert "Technical Assignment" in data["final_markdown"]
    assert data["cost_forecast_markdown"]
    assert data["safety"]["is_safe_to_export"] is True
