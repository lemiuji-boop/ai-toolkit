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

from app.pipeline.runner import run_analysis
from app.tasks.celery_app import celery_app


@celery_app.task(name="ai.analyze_pdf")
def analyze_pdf_task(payload: dict) -> dict:
    return run_analysis(payload.get("file_path", ""), doc_kind=payload.get("doc_kind", "kd"))
