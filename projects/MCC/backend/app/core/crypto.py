"""Шифрование API-ключей провайдеров (контракт §4 TZ-FINAL).
Fernet-ключ берётся из env SECRET_KEY (urlsafe base64, 32 байта)."""
import base64
import hashlib
import os

from cryptography.fernet import Fernet


def _fernet() -> Fernet:
    secret = os.environ.get("SECRET_KEY")
    if not secret:
        raise RuntimeError("SECRET_KEY is not set (required for API key encryption)")
    # Допускаем произвольную строку: нормализуем в 32-байтовый ключ.
    digest = hashlib.sha256(secret.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_key(plain: str) -> str:
    return _fernet().encrypt(plain.encode()).decode()


def decrypt_key(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()


def mask_key(plain: str) -> str:
    """Маска для UI/API: ••••last4 (контракт §4)."""
    tail = plain[-4:] if len(plain) >= 4 else plain
    return f"••••{tail}"
