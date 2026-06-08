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

from pdf2image import convert_from_path
import pytesseract


def pdf_to_text_ocr(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path, first_page=1, last_page=3)
    chunks: list[str] = []
    for img in pages:
        chunks.append(pytesseract.image_to_string(img, lang="rus", config="--psm 6"))
    return "\n".join(chunks)
