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

"""Проверка смены пароля и базовые заголовки безопасности."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth_service import decode_access_token_optional

EXEMPT_PATHS = frozenset(
    {
        "/health",
        "/auth/login",
        "/auth/refresh",
        "/auth/change-password",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
)


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path.rstrip("/") or "/"
        if path in EXEMPT_PATHS or path.startswith("/docs"):
            response = await call_next(request)
            return self._add_headers(response)

        token = _extract_bearer(request)
        if token:
            user_id = decode_access_token_optional(token)
            if user_id is not None and path not in {"/auth/me"}:
                blocked = await _user_must_change_password(int(user_id))
                if blocked:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "password_change_required"},
                    )

        response = await call_next(request)
        return self._add_headers(response)

    @staticmethod
    def _add_headers(response: Response) -> Response:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


def _extract_bearer(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


async def _user_must_change_password(user_id: int) -> bool:
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if user is None or not user.is_active:
            return False
        return bool(user.must_change_password)
