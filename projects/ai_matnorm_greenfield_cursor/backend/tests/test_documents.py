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

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, ExtractedFact, StoredFile, User


@pytest.mark.asyncio
async def test_fact_confirm_reject(client: AsyncClient, db_session: AsyncSession, seeded_db: User):
    sf = StoredFile(
        id=uuid.uuid4(),
        original_name="test.pdf",
        mime_type="application/pdf",
        size_bytes=100,
        storage_key="test/key",
        sha256="a" * 64,
        uploaded_by_id=seeded_db.id,
    )
    db_session.add(sf)
    await db_session.flush()
    doc = Document(
        id=uuid.uuid4(),
        file_id=sf.id,
        document_type="part_drawing",
        is_scan=False,
        has_text_layer=True,
        page_count=1,
        quality_score=0.9,
    )
    db_session.add(doc)
    await db_session.flush()
    fact = ExtractedFact(
        id=uuid.uuid4(),
        document_id=doc.id,
        field="material",
        value="АМг6",
        method="text_layer",
        confidence=0.8,
    )
    db_session.add(fact)
    await db_session.commit()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    confirm = await client.post(f"/api/v1/facts/{fact.id}/confirm", headers=headers)
    assert confirm.status_code == 200
    assert confirm.json()["review_status"] == "approved"

    reject = await client.post(f"/api/v1/facts/{fact.id}/reject", headers=headers)
    assert reject.status_code == 200
    assert reject.json()["review_status"] == "rejected"
