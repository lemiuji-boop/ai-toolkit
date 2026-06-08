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

def classify_document(filename: str, mime: str, data: bytes) -> tuple[str, bool, bool]:
    """Классификация типа документа (rule-based v1)."""
    name = filename.lower()
    if "специф" in name or "spec" in name:
        return "specification", False, True
    if "сбор" in name or "assembly" in name:
        return "assembly_drawing", True, False
    if name.endswith(".pdf"):
        has_text = b"/Font" in data[:50000] or len(data) < 500
        is_scan = not has_text
        return ("part_drawing" if not is_scan else "part_drawing_scan", is_scan, has_text)
    if name.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")):
        return "image_scan", True, False
    if name.endswith((".xls", ".xlsx")):
        return "excel_template", False, True
    if name.endswith((".doc", ".docx")):
        return "technical_requirements", False, True
    return "unknown", False, False
