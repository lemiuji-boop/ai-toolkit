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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import write_audit
from app.core.permissions import Perm, get_current_user, require_permission
from app.db.models import Calculation, Project, User
from app.db.session import get_db
from app.schemas.projects import (
    CalculationResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[Project]:
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    user: User = Depends(require_permission(Perm.PROJECTS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> Project:
    project = Project(id=uuid.uuid4(), name=body.name, description=body.description, owner_id=user.id)
    db.add(project)
    await write_audit(
        db, user_id=user.id, action="create", entity_type="project", entity_id=str(project.id)
    )
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> Project:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    user: User = Depends(require_permission(Perm.PROJECTS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> Project:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if body.name is not None:
        project.name = body.name
    if body.description is not None:
        project.description = body.description
    await write_audit(
        db, user_id=user.id, action="update", entity_type="project", entity_id=str(project.id)
    )
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}/calculations", response_model=list[CalculationResponse])
async def list_project_calculations(
    project_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_READ.value)),
    db: AsyncSession = Depends(get_db),
) -> list[Calculation]:
    result = await db.execute(
        select(Calculation)
        .where(Calculation.project_id == project_id)
        .order_by(Calculation.created_at.desc())
    )
    return list(result.scalars().all())


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    user: User = Depends(require_permission(Perm.PROJECTS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> None:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    await write_audit(
        db, user_id=user.id, action="delete", entity_type="project", entity_id=str(project.id)
    )
    await db.delete(project)
    await db.commit()
