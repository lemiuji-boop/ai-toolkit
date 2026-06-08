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

"""FR-020: модель job и события."""
import uuid
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.db.models import Job, JobStatus, User


@pytest.mark.asyncio
async def test_job_events_list(client: AsyncClient, db_session, seeded_db: User):
    job = Job(
        id=uuid.uuid4(),
        job_type="document-processing",
        status=JobStatus.PENDING,
        progress_percent=0,
        created_by_id=seeded_db.id,
    )
    db_session.add(job)
    await db_session.commit()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    token = login.json()["access_token"]
    r = await client.get(
        f"/api/v1/jobs/{job.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "pending"


@pytest.mark.asyncio
async def test_cancel_job(client: AsyncClient, db_session, seeded_db: User):
    job = Job(
        id=uuid.uuid4(),
        job_type="document-processing",
        status=JobStatus.RUNNING,
        progress_percent=50,
        created_by_id=seeded_db.id,
        rq_job_id="fake-rq-id",
    )
    db_session.add(job)
    await db_session.commit()

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "testpass123"},
    )
    token = login.json()["access_token"]

    with patch("rq.job.Job.fetch") as mock_fetch:
        mock_job = MagicMock()
        mock_fetch.return_value = mock_job
        r = await client.post(
                f"/api/v1/jobs/{job.id}/cancel",
                headers={"Authorization": f"Bearer {token}"},
            )
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"

    r2 = await client.get(
        f"/api/v1/jobs/{job.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.json()["status"] == "cancelled"
