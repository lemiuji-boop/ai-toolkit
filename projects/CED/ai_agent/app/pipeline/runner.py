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

"""Единый запуск пайплайна анализа PDF."""

from app.pipeline.classifier import classify_doc_type
from app.pipeline.extractor import extract_text, has_text_layer
from app.pipeline.ner import extract_fields
from app.pipeline.stamp_ii import extract_ii_form
from app.pipeline.stamp_kd import extract_kd_stamp
from app.pipeline.table_parser import extract_bom_rows
from app.services.llm_client import enrich_kd_fields_with_llm, ollama_available


def run_analysis(pdf_path: str, doc_kind: str = "kd") -> dict:
    if doc_kind == "ii":
        ii_data = extract_ii_form(pdf_path)
        return {
            "task_id": "sync",
            "status": "done",
            "data": ii_data,
            "quality": _quality(pdf_path),
        }

    kd_fields = extract_kd_stamp(pdf_path)
    ner_fields = extract_fields(extract_text(pdf_path))
    for key, value in ner_fields.items():
        if key not in kd_fields or not kd_fields[key].get("value"):
            kd_fields[key] = value

    full_text = extract_text(pdf_path)
    doc_type = classify_doc_type(full_text)
    kd_fields["doc_type"] = {"value": doc_type["doc_type"], "confidence": doc_type["confidence"]}
    bom_rows = extract_bom_rows(full_text)
    kd_fields["bom_rows"] = {"value": bom_rows, "confidence": 0.75 if bom_rows else 0.2}

    llm_used = False
    if ollama_available():
        kd_fields = enrich_kd_fields_with_llm(kd_fields, full_text)
        llm_used = True

    quality = _quality(pdf_path)
    quality["llm_available"] = llm_used

    return {
        "task_id": "sync",
        "status": "done",
        "data": kd_fields,
        "quality": quality,
    }


def _quality(pdf_path: str) -> dict:
    has_layer = has_text_layer(pdf_path)
    return {
        "has_text_layer": has_layer,
        "ocr_required": not has_layer,
        "pdf_quality_score": 0.95 if has_layer else 0.7,
    }
