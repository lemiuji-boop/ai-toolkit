"""Детерминированный эмбеддинг по хешированию токенов (bag-of-words).

Не загружает внешних моделей и не ходит в сеть (требование on-premise): вектор
строится из MD5-хешей токенов. Этого достаточно для скаффолда RAG; в продуктиве
заменяется на полноценную модель эмбеддингов (bge-m3 и т.п.) без смены интерфейса.
"""
from __future__ import annotations

import hashlib
import math
import re

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def embed(text: str, dim: int) -> list[float]:
    """Нормализованный вектор фиксированной размерности по токенам текста."""
    vec = [0.0] * dim
    for tok in _tokens(text):
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    """Косинусная близость двух нормализованных векторов (скалярное произведение)."""
    return sum(x * y for x, y in zip(a, b, strict=False))
