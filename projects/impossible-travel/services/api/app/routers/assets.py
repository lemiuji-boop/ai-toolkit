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

"""Ассеты."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.assets import Asset
from app.schemas.common import AssetResponse

router = APIRouter()


@router.get("", response_model=list[AssetResponse])
async def list_assets(
    episode_id: UUID | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[Asset]:
    """Список ассетов."""
    q = select(Asset).order_by(Asset.created_at.desc())
    if episode_id:
        q = q.where(Asset.episode_id == episode_id)
    result = await session.execute(q)
    return list(result.scalars().all())
