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

import re
import uuid

from app.db.models import ExtractedFact


def extract_facts_from_document(
    text: str,
    document_id: uuid.UUID,
    page: int,
    method: str = "text_layer",
) -> list[ExtractedFact]:
    """Rule-based извлечение инженерных фактов из текста."""
    facts: list[ExtractedFact] = []
    patterns = {
        "designation": r"(?:Обозначение|Designation)[:\s]+([^\n\r]+)",
        "name": r"(?:Наименование|Name)[:\s]+([^\n\r]+)",
        "material": r"(?:Материал|Material)[:\s]+([^\n\r]+)",
        "mass": r"(?:Масса|Mass)[:\s]+([0-9.,]+\s*(?:кг|kg)?)",
    }
    for field, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            value = m.group(1).strip()
            facts.append(
                ExtractedFact(
                    id=uuid.uuid4(),
                    document_id=document_id,
                    field=field,
                    value=value,
                    normalized_value=value.split()[0] if field == "material" else value,
                    source_page=page,
                    method=method,
                    confidence=0.85,
                    evidence_text=m.group(0)[:500],
                    created_by="system",
                )
            )
    return facts
