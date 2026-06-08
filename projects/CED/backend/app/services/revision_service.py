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

"""История редакций записей каталога."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.record_revision import RecordRevision, RevisionAction, RevisionTargetType
from app.models.user import User


async def record_revision(
    db: AsyncSession,
    *,
    target_type: RevisionTargetType,
    target_id: int,
    action: RevisionAction,
    changed_fields: dict,
    user: User | None = None,
    comment: str | None = None,
) -> RecordRevision:
    entry = RecordRevision(
        target_type=target_type,
        target_id=target_id,
        action=action,
        changed_fields=changed_fields,
        user_id=user.id if user else None,
        comment=comment,
    )
    db.add(entry)
    await db.flush()
    return entry
