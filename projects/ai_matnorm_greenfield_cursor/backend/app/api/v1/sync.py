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

"""Синхронизация desktop ↔ server."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import get_current_user
from app.db.models import SyncEvent, User
from app.db.session import get_db

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncEventResponse(BaseModel):
    id: uuid.UUID
    event_type: str
    payload: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncPushRequest(BaseModel):
    event_type: str
    payload: dict | None = None


@router.get("/events", response_model=list[SyncEventResponse])
async def list_sync_events(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SyncEvent]:
    result = await db.execute(
        select(SyncEvent)
        .where(SyncEvent.user_id == user.id)
        .order_by(SyncEvent.created_at.desc())
        .limit(100)
    )
    return list(result.scalars().all())


@router.post("/push", response_model=SyncEventResponse, status_code=201)
async def push_sync_event(
    body: SyncPushRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SyncEvent:
    event = SyncEvent(
        id=uuid.uuid4(),
        user_id=user.id,
        event_type=body.event_type,
        payload=body.payload,
        created_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
