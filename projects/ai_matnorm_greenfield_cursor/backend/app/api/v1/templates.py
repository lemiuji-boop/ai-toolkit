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

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.permissions import Perm, get_current_user, require_permission
from app.db.models import CalculationItem, ExcelExport, ExcelTemplate, KsiNode, User
from app.db.session import get_db
from app.services.excel_templates.export import export_materials_to_excel
from app.services.storage.s3 import get_storage

router = APIRouter(tags=["templates"])


class TemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    version: int
    field_mapping: dict | None = None

    model_config = {"from_attributes": True}


class FieldMappingUpdate(BaseModel):
    field_mapping: dict


class ExportRequest(BaseModel):
    calculation_id: uuid.UUID
    template_id: uuid.UUID | None = None


class ExportResponse(BaseModel):
    id: uuid.UUID
    download_url: str


@router.post("/templates/excel", response_model=TemplateResponse)
async def upload_template(
    file: UploadFile = File(...),
    user: User = Depends(require_permission(Perm.ADMIN.value)),
    db: AsyncSession = Depends(get_db),
) -> ExcelTemplate:
    data = await file.read()
    key, _ = get_storage().upload_bytes(data, content_type=file.content_type or "application/octet-stream")
    tpl = ExcelTemplate(
        id=uuid.uuid4(),
        name=file.filename or "template.xlsx",
        storage_key=key,
        field_mapping={},
    )
    db.add(tpl)
    await db.commit()
    await db.refresh(tpl)
    return tpl


@router.get("/templates/excel", response_model=list[TemplateResponse])
async def list_templates(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ExcelTemplate]:
    result = await db.execute(select(ExcelTemplate))
    return list(result.scalars().all())


@router.post("/exports/excel", response_model=ExportResponse)
async def export_excel(
    body: ExportRequest,
    user: User = Depends(require_permission(Perm.CALCULATIONS_WRITE.value)),
    db: AsyncSession = Depends(get_db),
) -> ExportResponse:
    items = (
        await db.execute(
            select(CalculationItem).where(CalculationItem.calculation_id == body.calculation_id)
        )
    ).scalars().all()
    template_bytes = None
    tpl = None
    if body.template_id:
        tpl = await db.get(ExcelTemplate, body.template_id)
        if tpl:
            template_bytes = get_storage().download_bytes(tpl.storage_key)

    rows = [
        {
            "designation": "",
            "material_name": i.material_name,
            "net_qty": i.net_qty,
            "gross_qty": i.gross_qty,
            "unit": i.unit,
        }
        for i in items
    ]
    mapping = tpl.field_mapping if body.template_id and tpl else None
    xlsx = export_materials_to_excel(template_bytes, rows, field_mapping=mapping)
    key, _ = get_storage().upload_bytes(
        xlsx, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    export = ExcelExport(
        id=uuid.uuid4(),
        calculation_id=body.calculation_id,
        template_id=body.template_id,
        storage_key=key,
    )
    db.add(export)
    await db.commit()
    url = get_storage().presigned_url(key)
    return ExportResponse(id=export.id, download_url=url)


@router.patch("/templates/excel/{template_id}/mapping", response_model=TemplateResponse)
async def update_template_mapping(
    template_id: uuid.UUID,
    body: FieldMappingUpdate,
    user: User = Depends(require_permission(Perm.ADMIN.value)),
    db: AsyncSession = Depends(get_db),
) -> ExcelTemplate:
    tpl = await db.get(ExcelTemplate, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    tpl.field_mapping = body.field_mapping
    await db.commit()
    await db.refresh(tpl)
    return tpl


@router.get("/exports/{export_id}/download", response_model=ExportResponse)
async def download_export(
    export_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ExportResponse:
    exp = await db.get(ExcelExport, export_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Экспорт не найден")
    return ExportResponse(id=exp.id, download_url=get_storage().presigned_url(exp.storage_key))
