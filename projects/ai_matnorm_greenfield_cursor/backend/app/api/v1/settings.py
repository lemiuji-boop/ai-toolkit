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

"""Настройки приложения (не секреты пользователя)."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import settings
from app.core.permissions import require_admin
from app.db.models import User

router = APIRouter(prefix="/settings", tags=["settings"])


class OcrSettingsResponse(BaseModel):
    ocr_provider: str


class OcrSettingsUpdate(BaseModel):
    ocr_provider: str


@router.get("/ocr", response_model=OcrSettingsResponse)
async def get_ocr_settings(_user: User = Depends(require_admin)) -> OcrSettingsResponse:
    return OcrSettingsResponse(ocr_provider=settings.ocr_provider)


@router.post("/ocr", response_model=OcrSettingsResponse)
async def set_ocr_settings(
    body: OcrSettingsUpdate,
    _user: User = Depends(require_admin),
) -> OcrSettingsResponse:
    # runtime override (dev); для prod — через .env и рестарт
    settings.ocr_provider = body.ocr_provider
    return OcrSettingsResponse(ocr_provider=settings.ocr_provider)
