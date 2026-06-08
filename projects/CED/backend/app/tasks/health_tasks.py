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

"""Ежедневная проверка зависших обработок и очередей."""

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.document_analysis import AnalysisStatus, DocumentAnalysis
from app.models.inbox_pending import InboxPending
from app.models.system_message import MessageSeverity
from app.services.error_agent_service import notify_staff
from app.tasks.celery_app import celery_app


@celery_app.task(name="daily_health_check")
def daily_health_check() -> dict:
    async def _run() -> dict:
        issues: list[str] = []
        async with AsyncSessionLocal() as db:
            pending = (
                await db.execute(
                    select(func.count(DocumentAnalysis.id)).where(
                        DocumentAnalysis.status == AnalysisStatus.pending
                    )
                )
            ).scalar_one()
            failed = (
                await db.execute(
                    select(func.count(DocumentAnalysis.id)).where(
                        DocumentAnalysis.status == AnalysisStatus.failed
                    )
                )
            ).scalar_one()
            inbox = (await db.execute(select(func.count(InboxPending.id)))).scalar_one()

            cutoff = datetime.now(timezone.utc) - timedelta(hours=4)
            stuck = (
                await db.execute(
                    select(func.count(DocumentAnalysis.id)).where(
                        DocumentAnalysis.status == AnalysisStatus.pending,
                        DocumentAnalysis.analyzed_at < cutoff,
                    )
                )
            ).scalar_one()

            if pending:
                issues.append(f"В очереди анализа: {pending}")
            if stuck:
                issues.append(f"Зависшие обработки (>4ч): {stuck}")
            if failed:
                issues.append(f"Ошибки анализа: {failed}")
            if inbox:
                issues.append(f"INBOX на ручной разбор: {inbox}")

            if issues:
                await notify_staff(
                    db,
                    title="Ежедневный отчёт CED",
                    body="Обнаружены проблемы:\n• " + "\n• ".join(issues),
                    severity=MessageSeverity.warning,
                    source="daily_health",
                )
                await db.commit()
        return {"issues": issues}

    return asyncio.run(_run())
