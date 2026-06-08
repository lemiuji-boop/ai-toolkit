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

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.activity import router as activity_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.admin import router as admin_router
from app.api.v1.calculation_files import router as calculation_files_router
from app.api.v1.auth import router as auth_router
from app.api.v1.calculations import router as calculations_router
from app.api.v1.documents import router as documents_router
from app.api.v1.files import router as files_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.ksi import router as ksi_router
from app.api.v1.materials import router as materials_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.reports import router as reports_router
from app.api.v1.settings import router as settings_router
from app.api.v1.sync import router as sync_router
from app.api.v1.projects import router as projects_router
from app.api.v1.templates import router as templates_router
from app.api.v1.users import router as users_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.rate_limit import rate_limit_middleware
from app.core.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="AI-МАТНОРМ API",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(BaseHTTPMiddleware, dispatch=rate_limit_middleware)
    application.add_middleware(SecurityHeadersMiddleware)

    prefix = settings.api_prefix
    routers = [
        health_router,
        auth_router,
        users_router,
        projects_router,
        calculations_router,
        files_router,
        jobs_router,
        documents_router,
        ksi_router,
        materials_router,
        templates_router,
        admin_router,
        monitoring_router,
        activity_router,
        calculation_files_router,
        assistant_router,
        reports_router,
        sync_router,
        settings_router,
    ]
    for r in routers:
        application.include_router(r, prefix=prefix)
    return application


app = create_app()
