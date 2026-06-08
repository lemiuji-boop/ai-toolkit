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

"""LLM-классификация и верификация документов."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.llm_outputs import DocumentClassificationOut
from app.services.llm_router.factory import build_router_from_db
from app.services.llm_router.router import LlmRequest, build_default_router


async def classify_document_with_llm(
    filename: str,
    text_sample: str,
    db: AsyncSession | None = None,
    local_only: bool = False,
) -> DocumentClassificationOut | None:
    """Классификация через LlmRouter с fallback на None."""
    sample = (text_sample or "")[:4000]
    prompt = (
        f"Определи тип инженерного документа по имени файла и фрагменту текста.\n"
        f"Файл: {filename}\n"
        f"Текст:\n{sample}\n"
        f"Верни JSON: document_type (part_drawing|assembly_drawing|specification|"
        f"technical_requirements|excel_template|unknown), confidence 0-1, language ru|en."
    )
    if local_only:
        return None
    router = await build_router_from_db(db) if db else build_default_router()
    try:
        resp = await router.run(
            LlmRequest(
                task_type="DOCUMENT_CLASSIFICATION",
                prompt=prompt,
                schema_model=DocumentClassificationOut,
            ),
            db=db,
        )
        if resp.parsed:
            return DocumentClassificationOut.model_validate(resp.parsed)
    except Exception:
        return None
    return None
