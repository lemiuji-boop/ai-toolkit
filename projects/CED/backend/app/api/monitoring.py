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

"""Мониторинг БД, сессий и очередей обработки."""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.config import settings
from app.core.database import get_db_session
from app.models.document import Document
from app.models.document_analysis import AnalysisStatus, DocumentAnalysis
from app.models.inbox_pending import InboxPending
from app.models.user import User, UserRole
from app.services.presence_service import list_active_sessions

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/overview")
async def monitoring_overview(
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role([UserRole.admin, UserRole.moderator])),
) -> dict:
    docs_total = (await db.execute(select(func.count(Document.id)).where(Document.deleted_at.is_(None)))).scalar_one()
    pending_analysis = (
        await db.execute(select(func.count(DocumentAnalysis.id)).where(DocumentAnalysis.status == AnalysisStatus.pending))
    ).scalar_one()
    failed_analysis = (
        await db.execute(select(func.count(DocumentAnalysis.id)).where(DocumentAnalysis.status == AnalysisStatus.failed))
    ).scalar_one()
    inbox_pending = (await db.execute(select(func.count(InboxPending.id)))).scalar_one()

    stale_cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
    stuck = (
        await db.execute(
            select(func.count(DocumentAnalysis.id)).where(
                DocumentAnalysis.status == AnalysisStatus.pending,
                DocumentAnalysis.analyzed_at < stale_cutoff,
            )
        )
    ).scalar_one()

    sessions = await list_active_sessions()

    ollama_status = await _probe_ai_agent_health()

    return {
        "ai": ollama_status,
        "database": {
            "documents": docs_total,
            "analysis_pending": pending_analysis,
            "analysis_failed": failed_analysis,
            "inbox_pending": inbox_pending,
            "stuck_processing": stuck,
        },
        "active_sessions": sessions,
        "active_count": len(sessions),
    }


async def _probe_ai_agent_health() -> dict[str, str | bool]:
    """Проверка ai-agent и доступности Ollama через туннель."""
    url = f"{settings.ai_agent_base_url.rstrip('/')}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "agent_reachable": True,
                    "ollama_available": bool(data.get("ollama_available")),
                    "ollama_url": str(data.get("ollama_url", "")),
                }
    except Exception:
        pass
    return {
        "agent_reachable": False,
        "ollama_available": False,
        "ollama_url": "",
    }
