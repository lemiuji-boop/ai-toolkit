"""Сессии админки (T-16, контракт §4): выпуск и проверка JWT.

Токен подписывается env SECRET_KEY (HS256), срок — settings.jwt_ttl_minutes.
Пароли и токены не логируются (SEC-002/003).
"""
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.core.config import settings


class TokenError(RuntimeError):
    """Невалидный или истёкший токен → API отдаёт 401."""

    code = "INVALID_TOKEN"


def issue_token(login: str, role: str = "admin") -> str:
    """Выпустить JWT для пользователя (sub=login, exp по TTL из настроек)."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": login,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_ttl_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def verify_token(token: str) -> dict[str, Any]:
    """Проверить подпись и срок токена; вернуть payload или TokenError."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise TokenError(f"токен отклонён: {type(exc).__name__}") from exc
