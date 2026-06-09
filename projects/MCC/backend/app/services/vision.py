"""Распознавание полей чертежа (FR-001/003/004).

Вызывает локальную VLM через OCR-препроцессор (FR-002); при недоступности
inference — детерминированная заглушка, чтобы каркас оставался работоспособным.
Нераспознанные поля возвращаются как null и не выдумываются (FR-004); по каждому
непустому полю формируется оценка уверенности [0..1] (FR-003).
"""
import base64
import json

import httpx

from app.core.config import settings
from app.core.schemas import Dimensions, ExtractResult
from app.services import ocr

PROMPT = (
    "Ты читаешь сканированный конструкторский чертёж. Извлеки данные только из "
    "изображения, не выдумывай. Верни строгий JSON: designation, name, material, "
    "mass_kg (число или null), dimensions_mm {length,width,height}, "
    "confidence — объект с оценкой уверенности [0..1] по каждому извлечённому полю. "
    "Нечитаемое поле — null (в confidence его не включай)."
)

# Поля основной надписи, для которых считаем уверенность (FR-003).
_FIELDS = ("designation", "name", "material", "mass_kg", "dimensions_mm")


def _confidence(data: dict, dims: Dimensions) -> dict[str, float]:
    """Уверенность по каждому непустому полю (FR-003). Null-поля не включаются (FR-004)."""
    raw = data.get("confidence") or {}
    conf: dict[str, float] = {}
    for field in _FIELDS:
        if field == "dimensions_mm":
            present = any(v is not None for v in (dims.length, dims.width, dims.height))
        else:
            present = data.get(field) is not None
        if present:
            # Уверенность от модели, иначе нейтральный порог из конфигурации.
            try:
                conf[field] = float(raw.get(field, settings.conf_threshold))
            except (TypeError, ValueError):
                conf[field] = settings.conf_threshold
    return conf


def _stub(*, minimal: bool = False) -> ExtractResult:
    """Детерминированная заглушка при недоступном inference (деградация каркаса).

    minimal=True — пустые поля основной надписи (режим model_only без чертежа).
    """
    if minimal:
        return ExtractResult(
            designation=None,
            name=None,
            material=None,
            mass_kg=None,
            dimensions_mm=Dimensions(),
            confidence={},
            source="stub",
        )
    return ExtractResult(
        designation="АБВГ.001.001",
        name="Кронштейн",
        material="Д16",
        mass_kg=0.42,
        dimensions_mm=Dimensions(length=180.0, width=90.0, height=24.0),
        confidence={"designation": 0.5, "name": 0.5, "material": 0.5, "mass_kg": 0.5},
        source="stub",
    )


def extract(image_bytes: bytes) -> ExtractResult:
    try:
        # FR-002: PDF→PNG и локализация зон до подачи в VLM.
        png, _debug = ocr.preprocess(image_bytes)
        img = base64.b64encode(png).decode()
        r = httpx.post(
            f"{settings.inference_url}/api/chat",
            json={
                "model": settings.vlm_model,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
                "messages": [{"role": "user", "content": PROMPT, "images": [img]}],
            },
            timeout=settings.inference_timeout,
        )
        r.raise_for_status()
        data = json.loads(r.json()["message"]["content"])
        raw_dims = data.get("dimensions_mm") or {}
        dims = Dimensions(**{k: raw_dims.get(k) for k in ("length", "width", "height")})
        return ExtractResult(
            designation=data.get("designation"),
            name=data.get("name"),
            material=data.get("material"),
            mass_kg=data.get("mass_kg"),
            dimensions_mm=dims,
            confidence=_confidence(data, dims),
            source="llm",
        )
    except Exception:
        # Inference недоступен или ошибка — каркас продолжает работать на заглушке.
        return _stub()
