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

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.security import SecurityMiddleware

from app.api import (
    admin,
    ai_providers,
    auth,
    catalog,
    change_orders,
    document_ai,
    documents,
    inbox,
    internal_ai,
    monitoring,
    relations,
    revisions,
    search,
    settings_api,
    system_messages,
)
from app.core.config import settings
from app.core.bootstrap import ensure_defaults
from app.services.inbox_watcher import start_inbox_watcher


logger = logging.getLogger(__name__)

_WEAK_SECRETS = frozenset({"change-me", "change-me-refresh", "change-me-ai"})


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    if settings.app_env == "production":
        if settings.jwt_secret_key in _WEAK_SECRETS or settings.ai_agent_api_key in _WEAK_SECRETS:
            logger.critical("Обнаружены слабые секреты в .env — смените перед эксплуатацией")
    await ensure_defaults()
    start_inbox_watcher()
    yield


app = FastAPI(title="CED Backend API", docs_url="/docs" if settings.debug else None, lifespan=lifespan)

app.add_middleware(SecurityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(document_ai.router, prefix="/documents")
app.include_router(search.router, tags=["search"])
app.include_router(relations.router, tags=["relations"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(catalog.router, tags=["catalog"])
app.include_router(change_orders.router, tags=["change-orders"])
app.include_router(inbox.router)
app.include_router(revisions.router)
app.include_router(ai_providers.router)
app.include_router(internal_ai.router)
app.include_router(settings_api.router)
app.include_router(monitoring.router)
app.include_router(system_messages.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
