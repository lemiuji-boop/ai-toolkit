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

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import write_audit
from app.core.permissions import get_current_user
from app.db.models import Document, ExtractedFact, User, UserCorrection
from app.db.session import get_db
from app.schemas.documents import DocumentResponse, FactResponse, FactUpdate

router = APIRouter(tags=["documents"])


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return doc


@router.get("/documents/{document_id}/facts", response_model=list[FactResponse])
async def list_facts(
    document_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ExtractedFact]:
    result = await db.execute(
        select(ExtractedFact).where(ExtractedFact.document_id == document_id)
    )
    return list(result.scalars().all())


@router.patch("/facts/{fact_id}", response_model=FactResponse)
async def update_fact(
    fact_id: uuid.UUID,
    body: FactUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractedFact:
    fact = await db.get(ExtractedFact, fact_id)
    if not fact:
        raise HTTPException(status_code=404, detail="Факт не найден")
    if fact.original_value is None:
        fact.original_value = fact.value
    old = fact.value
    fact.value = body.value
    fact.is_user_corrected = True
    fact.created_by = "manual"
    fact.method = "manual"
    fact.review_status = "pending"
    db.add(
        UserCorrection(
            id=uuid.uuid4(),
            fact_id=fact.id,
            user_id=user.id,
            old_value=old,
            new_value=body.value,
            reason=body.reason,
        )
    )
    await write_audit(
        db,
        user_id=user.id,
        action="fact_correct",
        entity_type="extracted_fact",
        entity_id=str(fact.id),
        payload={"old": old, "new": body.value},
    )
    await db.commit()
    await db.refresh(fact)
    return fact


@router.post("/facts/{fact_id}/confirm", response_model=FactResponse)
async def confirm_fact(
    fact_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractedFact:
    fact = await db.get(ExtractedFact, fact_id)
    if not fact:
        raise HTTPException(status_code=404, detail="Факт не найден")
    fact.review_status = "approved"
    from app.services.feedback_learning.rag import index_approved_fact

    index_approved_fact(
        fact.id,
        fact.field,
        fact.value,
        str(fact.document_id),
    )
    await write_audit(
        db,
        user_id=user.id,
        action="fact_confirm",
        entity_type="extracted_fact",
        entity_id=str(fact.id),
    )
    await db.commit()
    await db.refresh(fact)
    return fact


@router.post("/facts/{fact_id}/reject", response_model=FactResponse)
async def reject_fact(
    fact_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExtractedFact:
    fact = await db.get(ExtractedFact, fact_id)
    if not fact:
        raise HTTPException(status_code=404, detail="Факт не найден")
    fact.review_status = "rejected"
    await write_audit(
        db,
        user_id=user.id,
        action="fact_reject",
        entity_type="extracted_fact",
        entity_id=str(fact.id),
    )
    await db.commit()
    await db.refresh(fact)
    return fact
