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

"""APScheduler jobs for scheduled publishing."""
from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from bot.publisher import publish_post
from core.db import session_scope
from core.models import Post, PostStatus

_scheduler: AsyncIOScheduler | None = None


async def publish_due_posts() -> int:
    """Publish all approved posts whose scheduled_at <= now."""
    now = datetime.utcnow()
    count = 0
    async with session_scope() as session:
        result = await session.execute(
            select(Post).where(
                Post.status == PostStatus.approved,
                Post.scheduled_at.is_not(None),
                Post.scheduled_at <= now,
            )
        )
        for post in result.scalars().all():
            await publish_post(session, post)
            count += 1
    return count


def start_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
        _scheduler.add_job(publish_due_posts, "interval", minutes=5, id="publish_due")
        _scheduler.start()
    return _scheduler
