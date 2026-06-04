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

"""Editorial calendar and topic selection."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import CalendarSlot, ExperimentKind, Post

DEFAULT_SLOTS = [
    (0, "12:00", ExperimentKind.benchmark_roundup),
    (2, "19:00", ExperimentKind.head_to_head),
    (4, "19:00", ExperimentKind.fits_6gb),
    (5, "12:00", ExperimentKind.news),
]


async def seed_calendar(session: AsyncSession) -> int:
    """Insert default calendar slots if empty."""
    result = await session.execute(select(CalendarSlot))
    if result.scalars().first():
        return 0
    for weekday, time_local, rubric in DEFAULT_SLOTS:
        session.add(
            CalendarSlot(
                weekday=weekday,
                time_local=time_local,
                rubric=rubric,
                active=True,
            )
        )
    await session.flush()
    return len(DEFAULT_SLOTS)


async def pick_next_rubric(session: AsyncSession) -> ExperimentKind:
    """Choose rubric for today based on calendar; avoid recent duplicates."""
    now = datetime.now()
    weekday = now.weekday()
    result = await session.execute(
        select(CalendarSlot).where(
            CalendarSlot.weekday == weekday, CalendarSlot.active.is_(True)
        )
    )
    slot = result.scalars().first()
    if slot:
        return slot.rubric
    return ExperimentKind.model_review


async def recent_post_kinds(session: AsyncSession, limit: int = 5) -> list[ExperimentKind]:
    result = await session.execute(
        select(Post.kind).order_by(Post.id.desc()).limit(limit)
    )
    return list(result.scalars().all())
