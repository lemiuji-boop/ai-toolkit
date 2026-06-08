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

"""Настройки пользователя и справка по каталогу."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db_session
from app.models.user import User
from app.models.user_preference import UserPreference
from app.services.storage_access import storage, StorageAccessMode

router = APIRouter(prefix="/settings", tags=["settings"])


class PreferencesIn(BaseModel):
    theme_id: str | None = None
    dark_mode: bool | None = None
    catalog_root_hint: str | None = None


class PreferencesOut(BaseModel):
    theme_id: str
    dark_mode: bool
    catalog_root_hint: str | None
    server_catalog_root: str
    api_base_url: str
    storage_mode: str
    inbox_subdir: str


@router.get("/preferences", response_model=PreferencesOut)
async def get_preferences(
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> PreferencesOut:
    row = await db.get(UserPreference, user.id)
    if row is None:
        row = UserPreference(user_id=user.id)
        db.add(row)
        await db.commit()
        await db.refresh(row)
    mode = storage.check_access()
    return PreferencesOut(
        theme_id=row.theme_id,
        dark_mode=row.dark_mode,
        catalog_root_hint=row.catalog_root_hint,
        server_catalog_root=str(settings.catalog_root),
        api_base_url="/api",
        storage_mode=mode.value,
        inbox_subdir=settings.inbox_subdir,
    )


@router.put("/preferences", response_model=PreferencesOut)
async def update_preferences(
    payload: PreferencesIn,
    db: AsyncSession = Depends(get_db_session),
    user: User = Depends(get_current_user),
) -> PreferencesOut:
    row = await db.get(UserPreference, user.id)
    if row is None:
        row = UserPreference(user_id=user.id)
        db.add(row)
    if payload.theme_id is not None:
        row.theme_id = payload.theme_id
    if payload.dark_mode is not None:
        row.dark_mode = payload.dark_mode
    if payload.catalog_root_hint is not None:
        row.catalog_root_hint = payload.catalog_root_hint or None
    await db.commit()
    await db.refresh(row)
    mode = storage.check_access()
    return PreferencesOut(
        theme_id=row.theme_id,
        dark_mode=row.dark_mode,
        catalog_root_hint=row.catalog_root_hint,
        server_catalog_root=str(settings.catalog_root),
        api_base_url="/api",
        storage_mode=mode.value,
        inbox_subdir=settings.inbox_subdir,
    )


@router.get("/catalog-help")
async def catalog_help(_: User = Depends(get_current_user)) -> dict:
    """Справка: зачем корень каталога и API."""
    return {
        "catalog_root_title": "Корень каталога (UNC)",
        "catalog_root_text": (
            "Это сетевая папка, где физически лежат PDF КД и извещения. "
            "Сервер монтирует её как CATALOG_ROOT (в Docker: /data/catalog). "
            "Поле в настройках — подсказка для клиента/desktop: куда копировать файлы в _INBOX. "
            "Backend сам пишет в каталог только при READ_WRITE."
        ),
        "api_title": "Адрес API",
        "api_text": (
            "Веб-клиент ходит на /api (nginx → backend). "
            "Desktop указывает полный URL (http://host:80/api или http://localhost/api). "
            "Через API: авторизация, каталог, загрузка, ИИ-анализ, мониторинг, уведомления."
        ),
        "inbox_title": "Разбор INBOX",
        "inbox_text": (
            "Папка _INBOX в корне каталога — «входящие». "
            "Watcher/Celery забирает новые PDF, отправляет в ИИ-агент, "
            "при уверенности ≥ порога раскладывает по catalog/… или _ИИ/…, "
            "иначе оставляет в очереди needs_review для модератора."
        ),
    }
