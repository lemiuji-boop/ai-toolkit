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

import httpx

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.analysis_service import create_pending_analysis, save_analysis_result
from app.services.error_agent_service import handle_processing_failure
from app.tasks.celery_app import celery_app


@celery_app.task(name="analyze_document")
def analyze_document(file_path: str, version_id: int, doc_kind: str = "kd") -> dict[str, str | int]:
    async def _run() -> dict:
        async with AsyncSessionLocal() as session:
            await create_pending_analysis(session, version_id)
            await session.commit()

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.ai_agent_base_url}/analyze",
                    json={"file_path": file_path, "doc_kind": doc_kind},
                    headers={"X-API-Key": settings.ai_agent_api_key},
                )
                response.raise_for_status()
                payload = response.json()

            async with AsyncSessionLocal() as session:
                await save_analysis_result(session, version_id, payload)
                await session.commit()
            return {"version_id": version_id, "status": "done"}
        except Exception as exc:  # noqa: BLE001
            err = str(exc)
            async with AsyncSessionLocal() as session:
                await save_analysis_result(
                    session, version_id, {}, failed=True, error_message=err
                )
                await handle_processing_failure(
                    session,
                    context="анализ документа",
                    error_text=err,
                    file_path=file_path,
                    doc_kind=doc_kind,
                )
                await session.commit()
            return {"version_id": version_id, "status": "failed", "error": err}

    return asyncio.run(_run())
