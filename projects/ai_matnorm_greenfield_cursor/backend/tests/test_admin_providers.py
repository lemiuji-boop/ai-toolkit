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

"""FR-070–FR-074: провайдеры ИИ и шифрование ключей."""
import uuid

import pytest
from httpx import AsyncClient

from app.core.encryption import decrypt_secret, encrypt_secret


def test_encrypt_roundtrip():
    raw = "sk-test-key-12345"
    enc = encrypt_secret(raw)
    assert decrypt_secret(enc) == raw
    assert raw not in enc


@pytest.mark.asyncio
async def test_create_and_test_provider(client: AsyncClient):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post(
        "/api/v1/admin/ai-providers",
        headers=headers,
        json={
            "name": f"mock-{uuid.uuid4().hex[:6]}",
            "provider_type": "mock",
            "is_enabled": True,
            "priority": 1,
        },
    )
    assert create.status_code == 201
    pid = create.json()["id"]

    test = await client.post(
        f"/api/v1/admin/ai-providers/{pid}/test-connection",
        headers=headers,
    )
    assert test.status_code == 200
    assert test.json()["status"] in ("valid", "error")
