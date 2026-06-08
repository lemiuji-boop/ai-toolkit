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

"""Анализ технологических признаков (детерминированные правила)."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ExtractedFact, ProcessRule


async def detect_process_type(db: AsyncSession, document_id: uuid.UUID) -> str:
    facts = (
        await db.execute(select(ExtractedFact).where(ExtractedFact.document_id == document_id))
    ).scalars().all()
    text = " ".join(f.value.lower() for f in facts)
    if "лист" in text or "sheet" in text:
        return "sheet_metal"
    if "токар" in text:
        return "turning"
    if "фрез" in text:
        return "milling"
    rules = (await db.execute(select(ProcessRule))).scalars().all()
    for r in rules:
        if r.material_type in text:
            return r.process_type
    return "cutting"
