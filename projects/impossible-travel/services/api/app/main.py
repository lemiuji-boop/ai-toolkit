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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.seed import seed_database
from app.db.session import async_session_factory
from app.routers import analytics, assets, characters, episodes, health, locations, tasks
from app.routers import settings as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Старт: seed БД."""
    async with async_session_factory() as session:
        await seed_database(session)
    yield


def create_app() -> FastAPI:
    """Фабрика приложения."""
    settings = get_settings()
    app = FastAPI(
        title="Impossible Travel AI API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(episodes.router, prefix="/episodes", tags=["episodes"])
    app.include_router(characters.router, prefix="/characters", tags=["characters"])
    app.include_router(locations.router, prefix="/locations", tags=["locations"])
    app.include_router(assets.router, prefix="/assets", tags=["assets"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
    app.include_router(settings_router.router, prefix="/settings", tags=["settings"])
    return app


app = create_app()
