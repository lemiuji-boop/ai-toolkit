"""Распознавание полей чертежа (FR-001/003/004) через router(confidential).

Без локального провайдера — VisionUnavailableError (TZ-FINAL §3), не заглушка.
Нераспознанные поля — null (FR-004); уверенность [0..1] по непустым полям (FR-003).
"""
import base64

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.schemas import Dimensions, ExtractResult
from app.services import ocr
from app.services.errors import VisionUnavailableError
from app.services.llm.base import DataClass
from app.services.llm.registry import list_providers
from app.services.llm.router import NoLocalProviderError, choose
from app.services.llm.structured import StructuredCallError, call_structured

PROMPT = (
    "Ты читаешь сканированный конструкторский чертёж. Извлеки данные только из "
    "изображения, не выдумывай. Нечитаемое поле — null."
)

_FIELDS = ("designation", "name", "material", "mass_kg", "dimensions_mm")


class _VisionOut(BaseModel):
    """Схема ответа модели для call_structured (TZ-FINAL §2.1)."""

    designation: str | None = None
    name: str | None = None
    material: str | None = None
    mass_kg: float | None = None
    dimensions_mm: Dimensions = Field(default_factory=Dimensions)
    confidence: dict[str, float] = Field(default_factory=dict)


def empty_extract() -> ExtractResult:
    """Пустое извлечение, когда чертёж не передан (режим model_only)."""
    return ExtractResult(
        designation=None,
        name=None,
        material=None,
        mass_kg=None,
        dimensions_mm=Dimensions(),
        confidence={},
        source="none",
    )


def _confidence(data: _VisionOut, dims: Dimensions) -> dict[str, float]:
    """Уверенность по каждому непустому полю (FR-003)."""
    raw = data.confidence or {}
    conf: dict[str, float] = {}
    for field in _FIELDS:
        if field == "dimensions_mm":
            present = any(v is not None for v in (dims.length, dims.width, dims.height))
        else:
            present = getattr(data, field) is not None
        if present:
            try:
                conf[field] = float(raw.get(field, settings.conf_threshold))
            except (TypeError, ValueError):
                conf[field] = settings.conf_threshold
    return conf


def _to_result(data: _VisionOut, *, source: str, model_version: str | None = None) -> ExtractResult:
    dims = data.dimensions_mm
    return ExtractResult(
        designation=data.designation,
        name=data.name,
        material=data.material,
        mass_kg=data.mass_kg,
        dimensions_mm=dims,
        confidence=_confidence(data, dims),
        source=source,
        model_version=model_version,
    )


async def extract(image_bytes: bytes) -> ExtractResult:
    """Извлечение полей чертежа; confidential-маршрут только на local-провайдер."""
    try:
        provider = choose(DataClass.confidential, list_providers)
    except NoLocalProviderError as exc:
        raise VisionUnavailableError(str(exc), code="NO_LOCAL_PROVIDER") from exc

    png, _debug = ocr.preprocess(image_bytes)
    img_b64 = base64.b64encode(png).decode()
    try:
        out = await call_structured(provider, PROMPT, _VisionOut, image_b64=img_b64)
    except StructuredCallError as exc:
        raise VisionUnavailableError(
            f"модель не вернула валидный JSON: {exc}",
            code="VISION_SCHEMA_ERROR",
        ) from exc
    except Exception as exc:
        raise VisionUnavailableError(
            f"ошибка вызова vision-провайдера: {exc}",
        ) from exc

    return _to_result(out, source="llm", model_version=provider.info.model)
