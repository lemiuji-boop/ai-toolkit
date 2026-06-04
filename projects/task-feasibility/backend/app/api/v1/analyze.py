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

"""Эндпоинты анализа задач."""

from fastapi import APIRouter, HTTPException

from app.agents.graph import run_analysis
from app.guardrails.shield import SafetyShield
from app.llm.router import LLMRouter
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse

router = APIRouter(tags=["analyze"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Анализ задачи MATFES",
    description="Маршрутизация L1–L4, feasibility, оценка токенов и генерация техзадания.",
)
async def analyze_task(body: AnalyzeRequest) -> AnalyzeResponse:
    """Запуск полного пайплайна."""
    shield = SafetyShield()
    safety = shield.scan(body.task)

    if safety.hard_blocked:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Обнаружены credentials или секреты. Запрос заблокирован.",
                "detected_violations": safety.detected_violations,
                "safety": safety.model_dump(),
            },
        )

    try:
        result = await run_analysis(
            task=body.task,
            project_name=body.project_name,
            context_lines=body.context_lines,
            safety=safety,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AnalyzeResponse(
        complexity_level=result["complexity_level"],  # type: ignore[arg-type]
        feasibility_score=result["feasibility_score"],
        is_feasible=result["is_feasible"],
        modified_options=result.get("modified_options", []),
        estimated_tokens=result.get("estimated_tokens", {}),
        cost_forecast_markdown=result.get("cost_forecast_markdown", ""),
        final_markdown=result.get("final_markdown", ""),
        safety=result["safety"],
        selected_stack=result.get("selected_stack", {}),
        warnings=result.get("warnings", []),
    )


@router.get("/models", summary="Статус LLM-провайдеров")
async def list_models() -> dict:
    """Проверка Ollama и облачного API."""
    llm_router = LLMRouter()
    return await llm_router.health()
