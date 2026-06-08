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

"""Вопросы ассистента по расчёту."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Perm, require_permission
from app.db.models import AssistantQuestion, User
from app.db.session import get_db

router = APIRouter(prefix="/assistant", tags=["assistant"])


class QuestionResponse(BaseModel):
    id: uuid.UUID
    calculation_id: uuid.UUID
    question: str
    status: str
    answer: str | None
    context: dict | None

    model_config = {"from_attributes": True}


class AnswerBody(BaseModel):
    answer: str


@router.get("/calculations/{calculation_id}/questions", response_model=list[QuestionResponse])
async def list_questions(
    calculation_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[AssistantQuestion]:
    result = await db.execute(
        select(AssistantQuestion)
        .where(AssistantQuestion.calculation_id == calculation_id)
        .order_by(AssistantQuestion.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/questions/{question_id}/answer", response_model=QuestionResponse)
async def answer_question(
    question_id: uuid.UUID,
    body: AnswerBody,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> AssistantQuestion:
    q = await db.get(AssistantQuestion, question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    q.answer = body.answer
    q.status = "answered"
    q.answered_by_id = user.id
    await db.commit()
    await db.refresh(q)
    return q
