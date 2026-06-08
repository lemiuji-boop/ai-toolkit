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

import asyncio
from pathlib import Path

from app.services.inbox_service import ingest_file
from app.services.storage_access import StorageAccessMode, storage
from app.tasks.celery_app import celery_app


@celery_app.task(name="inbox.ingest_file")
def ingest_file_task(file_path: str) -> dict:
    from app.core.database import AsyncSessionLocal

    async def _run() -> dict:
        async with AsyncSessionLocal() as session:
            result = await ingest_file(session, file_path, storage)
            await session.commit()
            return result

    return asyncio.run(_run())


@celery_app.task(name="inbox.scan")
def scan_inbox_task() -> dict:
    if storage.check_access() != StorageAccessMode.READ_WRITE:
        return {"status": "skipped", "reason": "read_only"}

    inbox = storage.inbox_path()
    if not inbox.exists():
        return {"status": "empty"}

    queued = 0
    for path in inbox.glob("**/*"):
        if path.is_file() and not path.name.startswith("."):
            ingest_file_task.delay(str(path))
            queued += 1
    return {"status": "queued", "count": queued}
