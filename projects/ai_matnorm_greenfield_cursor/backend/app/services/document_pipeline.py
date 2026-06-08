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

"""Пайплайн Document Intelligence v1."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import AssistantQuestion, Document, ExtractedFact, Job, Page, StoredFile
from app.services.document_classifier import classify_document
from app.services.fact_extraction import extract_facts_from_document
from app.services.layout_analysis.extractor import extract_tables_from_text
from app.services.llm_router.classify import classify_document_with_llm
from app.services.ocr.provider import get_ocr_provider
from app.services.storage.s3 import get_storage
from app.services.text_extraction import extract_text_from_file


def _render_pdf_page_image(pdf_bytes: bytes, page_index: int) -> bytes | None:
    try:
        import fitz

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if page_index >= len(doc):
            return None
        return doc[page_index].get_pixmap(dpi=150).tobytes("png")
    except Exception:
        return None


def _ocr_image_bytes(image_bytes: bytes) -> str:
    return get_ocr_provider().recognize_page(image_bytes).text


async def run_document_pipeline(
    db: AsyncSession, stored_file: StoredFile, job: Job
) -> Document:
    storage = get_storage()
    bucket = settings.s3_bucket_quarantine if stored_file.is_quarantined else settings.s3_bucket
    data = storage.download_bytes(stored_file.storage_key, bucket=bucket)

    doc_type, is_scan, has_text = classify_document(
        stored_file.original_name, stored_file.mime_type, data
    )
    text_pages = extract_text_from_file(stored_file.original_name, data)
    name_lower = stored_file.original_name.lower()

    if not text_pages and (
        is_scan or name_lower.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"))
    ):
        if name_lower.endswith(".pdf"):
            text_pages = []
            try:
                import fitz

                pdf = fitz.open(stream=data, filetype="pdf")
                for i in range(len(pdf)):
                    img = _render_pdf_page_image(data, i)
                    text_pages.append(_ocr_image_bytes(img) if img else "")
            except Exception:
                text_pages = [_ocr_image_bytes(data)]
        else:
            text_pages = [_ocr_image_bytes(data)]

    combined_text = "\n".join(text_pages)
    llm_cls = await classify_document_with_llm(
        stored_file.original_name, combined_text, db=db
    )
    language = llm_cls.language if llm_cls and llm_cls.confidence >= 0.5 else "ru"
    if llm_cls and llm_cls.confidence >= 0.5:
        doc_type = llm_cls.document_type

    doc = Document(
        id=uuid.uuid4(),
        file_id=stored_file.id,
        document_type=doc_type,
        is_scan=is_scan or not has_text,
        has_text_layer=bool(text_pages and any(t.strip() for t in text_pages)),
        language=language,
        page_count=max(len(text_pages), 1),
        quality_score=0.85 if text_pages and any(t.strip() for t in text_pages) else 0.45,
    )
    db.add(doc)
    await db.flush()

    method = "ocr" if is_scan or not has_text else "text_layer"
    low_confidence_material = False
    pages_text = text_pages if text_pages else [""]

    for i, page_text in enumerate(pages_text):
        db.add(Page(id=uuid.uuid4(), document_id=doc.id, page_number=i + 1))
        if not page_text.strip():
            continue
        for f in extract_facts_from_document(page_text, doc.id, i + 1, method=method):
            db.add(f)
            if f.field == "material" and f.confidence < 0.75:
                low_confidence_material = True
        if doc.document_type == "specification":
            for row in extract_tables_from_text(doc.id, page_text, i + 1):
                db.add(row)

    if not any(p.strip() for p in pages_text):
        db.add(
            ExtractedFact(
                id=uuid.uuid4(),
                document_id=doc.id,
                field="note",
                value="Не удалось извлечь текст",
                method="ocr",
                confidence=0.2,
                source_page=1,
                created_by="system",
            )
        )
        if job.calculation_id:
            db.add(
                AssistantQuestion(
                    id=uuid.uuid4(),
                    calculation_id=job.calculation_id,
                    question=(
                        f"Не удалось распознать «{stored_file.original_name}». "
                        "Загрузите PDF с текстовым слоем?"
                    ),
                    context={"file_id": str(stored_file.id), "document_id": str(doc.id)},
                )
            )

    if low_confidence_material and job.calculation_id:
        db.add(
            AssistantQuestion(
                id=uuid.uuid4(),
                calculation_id=job.calculation_id,
                question="Материал распознан с низкой уверенностью. Уточните марку материала.",
                context={"document_id": str(doc.id)},
            )
        )

    storage.move_to_main(stored_file.storage_key)
    stored_file.is_quarantined = False
    return doc
