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

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import settings
from app.core.path_security import resolve_allowed_path
from app.pipeline.runner import run_analysis
from app.tasks.jobs import analyze_pdf_task

router = APIRouter()


def verify_api_key(x_api_key: str = Header(default="")) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@router.post("/analyze")
async def analyze(payload: dict, _: None = Depends(verify_api_key)) -> dict:
    raw_path = payload.get("file_path", "")
    doc_kind = payload.get("doc_kind", "kd")
    pdf_path = str(resolve_allowed_path(str(raw_path)))
    return run_analysis(pdf_path, doc_kind=doc_kind)


@router.post("/analyze-async")
async def analyze_async(payload: dict, _: None = Depends(verify_api_key)) -> dict[str, str]:
    task = analyze_pdf_task.delay(payload)
    return {"task_id": task.id}


@router.get("/result/{task_id}")
async def result(task_id: str, _: None = Depends(verify_api_key)) -> dict:
    async_result = analyze_pdf_task.AsyncResult(task_id)
    if async_result.ready():
        return async_result.result or {"task_id": task_id, "status": "done"}
    return {"task_id": task_id, "status": "pending"}
