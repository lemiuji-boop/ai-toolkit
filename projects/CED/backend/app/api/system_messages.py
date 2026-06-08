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

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db_session
from app.models.system_message import SystemMessage
from app.models.user import User

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("")
async def list_messages(
    limit: int = Query(default=30, le=100),
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> list[dict]:
    stmt = select(SystemMessage).order_by(desc(SystemMessage.id)).limit(limit)
    rows = (await db.execute(stmt)).scalars().all()
    role = user.role.value if hasattr(user.role, "value") else str(user.role)
    result = []
    for row in rows:
        targets = [r.strip() for r in row.target_roles.split(",")]
        if role not in targets and role != "admin":
            continue
        result.append(
            {
                "id": row.id,
                "title": row.title,
                "body": row.body,
                "severity": row.severity.value,
                "source": row.source,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
        )
    return result
