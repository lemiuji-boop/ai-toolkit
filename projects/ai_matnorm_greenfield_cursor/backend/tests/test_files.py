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

"""FR-012–FR-013: загрузка файлов."""
import io
import uuid
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.db.models import Calculation, Project, User


@pytest.mark.asyncio
async def test_upload_txt_file(client: AsyncClient, db_session, seeded_db: User):
    proj = Project(id=uuid.uuid4(), name="P", owner_id=seeded_db.id)
    calc = Calculation(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="C",
        created_by_id=seeded_db.id,
    )
    db_session.add(proj)
    db_session.add(calc)
    await db_session.commit()

    mock_storage = MagicMock()
    mock_storage.upload_bytes.return_value = ("test-key", "abc123")

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    token = login.json()["access_token"]

    with patch("app.api.v1.files.get_storage", return_value=mock_storage):
        r = await client.post(
            "/api/v1/files/upload",
            headers={"Authorization": f"Bearer {token}"},
            data={"calculation_id": str(calc.id)},
            files={"files": ("spec.pdf", io.BytesIO(b"%PDF-1.4 test"), "application/pdf")},
        )
    assert r.status_code == 200
    body = r.json()
    assert len(body) >= 1
    assert body[0]["original_name"] == "spec.pdf"
    assert body[0]["is_quarantined"] is True
