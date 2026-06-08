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

from io import BytesIO


def extract_text_from_file(filename: str, data: bytes) -> list[str]:
    """Извлечение текстового слоя из PDF/DOCX."""
    name = filename.lower()
    if name.endswith(".pdf"):
        try:
            import fitz

            doc = fitz.open(stream=data, filetype="pdf")
            return [page.get_text() for page in doc]
        except Exception:
            try:
                import pdfplumber

                with pdfplumber.open(BytesIO(data)) as pdf:
                    return [p.extract_text() or "" for p in pdf.pages]
            except Exception:
                return []
    if name.endswith(".docx"):
        try:
            from docx import Document

            doc = Document(BytesIO(data))
            return ["\n".join(p.text for p in doc.paragraphs)]
        except Exception:
            return []
    return []
