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

"""Точка входа FastAPI."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import analyze as analyze_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Жизненный цикл приложения."""
    yield


def create_app() -> FastAPI:
    """Фабрика приложения FastAPI."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        description=(
            "Multi-Agent Task Feasibility & Estimation System — "
            "анализ задач, оценка feasibility и генерация техзаданий"
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(analyze_router.router, prefix=settings.api_prefix)
    return application


app = create_app()


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Проверка доступности сервиса."""
    return {"status": "ok", "service": get_settings().app_name}
