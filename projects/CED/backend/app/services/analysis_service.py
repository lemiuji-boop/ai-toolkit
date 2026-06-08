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

"""Сохранение и чтение результатов анализа ИИ."""

from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_analysis import AnalysisStatus, DocumentAnalysis


def extract_insight(extracted_data: dict) -> str | None:
    if not extracted_data:
        return None
    if extracted_data.get("insight"):
        return str(extracted_data["insight"])
    bom = extracted_data.get("bom_rows", {})
    if isinstance(bom, dict) and bom.get("value"):
        return "Обнаружены строки спецификации для проверки"
    doc_num = extracted_data.get("doc_number", {})
    if isinstance(doc_num, dict) and doc_num.get("confidence", 0) < 0.7:
        return "Низкая уверенность распознавания обозначения"
    return "Анализ завершён без критических замечаний"


async def create_pending_analysis(db: AsyncSession, version_id: int) -> DocumentAnalysis:
    row = DocumentAnalysis(
        version_id=version_id,
        status=AnalysisStatus.pending,
        extracted_data={},
        confidence={},
        analyzed_at=datetime.now(timezone.utc),
    )
    db.add(row)
    await db.flush()
    return row


async def save_analysis_result(
    db: AsyncSession,
    version_id: int,
    payload: dict,
    *,
    failed: bool = False,
    error_message: str | None = None,
) -> DocumentAnalysis:
    data = payload.get("data", {})
    if isinstance(data, dict) and "insight" not in data:
        insight = extract_insight(data)
        if insight:
            data = {**data, "insight": insight}

    status = AnalysisStatus.failed if failed else AnalysisStatus.done
    row = DocumentAnalysis(
        version_id=version_id,
        status=status,
        extracted_data=data if isinstance(data, dict) else {},
        confidence=payload.get("quality", {}),
        analyzed_at=datetime.now(timezone.utc),
        error_message=error_message,
    )
    db.add(row)
    await db.flush()
    return row


async def get_latest_analysis(db: AsyncSession, version_id: int | None) -> DocumentAnalysis | None:
    if not version_id:
        return None
    stmt = (
        select(DocumentAnalysis)
        .where(DocumentAnalysis.version_id == version_id)
        .order_by(desc(DocumentAnalysis.id))
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


def analysis_to_ui_status(
    analysis: DocumentAnalysis | None,
    *,
    has_version: bool = True,
    ocr_processed: bool | None = None,
) -> dict:
    """Коды для UI: uploaded (зелёный), processing (оранжевый), error (красный), loaded (зелёный)."""
    if not has_version:
        return {"label": "Нет файла", "code": "error", "percent": 0}
    if analysis is None:
        if ocr_processed is False:
            return {"label": "Загружен", "code": "uploaded", "percent": 0}
        return {"label": "Загружен", "code": "uploaded", "percent": 0}
    if analysis.status == AnalysisStatus.failed:
        return {"label": "Ошибка", "code": "error", "percent": 0}
    if analysis.status == AnalysisStatus.pending:
        return {"label": "Обрабатывается", "code": "processing", "percent": 50}
    conf = analysis.extracted_data or {}
    score = 98
    if isinstance(conf, dict):
        doc_num = conf.get("doc_number")
        if isinstance(doc_num, dict) and doc_num.get("confidence"):
            score = int(float(doc_num["confidence"]) * 100)
    return {"label": f"Обработан ({score}%)", "code": "loaded", "percent": score}
