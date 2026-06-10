"""Тесты распознавания (FR-001/002/003/004) — без GPU и без реального LLM."""
import importlib.util
import json

import pytest

from app.services import ocr, vision
from app.services.llm.base import ProviderInfo
from app.services.llm.registry import set_providers_fn

_HAS_FITZ = importlib.util.find_spec("fitz") is not None


class _FakeProvider:
    def __init__(self, payload: dict):
        self.info = ProviderInfo(
            id=1, name="fake", kind="local", base_url="http://x",
            model="m", enabled=True, priority=1,
        )
        self._payload = payload

    async def chat_text(self, prompt: str) -> str:
        return json.dumps(self._payload, ensure_ascii=False)

    async def chat_vision(self, prompt: str, image_b64: str) -> str:
        return await self.chat_text(prompt)


def _patch_provider(payload: dict) -> None:
    set_providers_fn(lambda: [_FakeProvider(payload)])


@pytest.mark.asyncio
async def test_extract_llm_success_with_confidence():
    _patch_provider({
        "designation": "АБВГ.123.456",
        "name": "Нервюра",
        "material": "АМг6",
        "mass_kg": 0.31,
        "dimensions_mm": {"length": 200, "width": 120, "height": 8},
        "confidence": {"designation": 0.95, "material": 0.88},
    })
    res = await vision.extract(b"\x89PNG\r\n")
    assert res.source == "llm"
    assert res.material == "АМг6"
    assert res.confidence["designation"] == 0.95
    assert res.confidence["mass_kg"] == vision.settings.conf_threshold
    assert "dimensions_mm" in res.confidence


@pytest.mark.asyncio
async def test_fr004_unreadable_fields_stay_null():
    _patch_provider({
        "designation": "АБВГ.999.000",
        "name": None,
        "material": None,
        "mass_kg": None,
        "dimensions_mm": {"length": None, "width": None, "height": None},
        "confidence": {"designation": 0.9},
    })
    res = await vision.extract(b"img")
    assert res.material is None
    assert res.mass_kg is None
    assert "material" not in res.confidence
    assert "mass_kg" not in res.confidence
    assert "dimensions_mm" not in res.confidence
    assert res.confidence["designation"] == 0.9


@pytest.mark.asyncio
async def test_extract_raises_without_local_provider():
    set_providers_fn(lambda: [])
    from app.services.errors import VisionUnavailableError

    with pytest.raises(VisionUnavailableError) as exc:
        await vision.extract(b"img")
    assert exc.value.code == "NO_LOCAL_PROVIDER"


def test_ocr_preprocess_png_passthrough_and_zones():
    png, debug = ocr.preprocess(b"\x89PNG\r\n\x1a\n")
    assert debug["source_was_pdf"] is False
    assert "title_block" in debug["zones"]
    assert len(debug["zones"]["title_block"]) == 4


def test_ocr_detects_pdf_signature():
    assert ocr.is_pdf(b"%PDF-1.7\n...") is True
    assert ocr.is_pdf(b"\x89PNG") is False


@pytest.mark.skipif(not _HAS_FITZ, reason="PyMuPDF не установлен")
def test_ocr_pdf_to_png_converts():
    import fitz

    doc = fitz.open()
    doc.new_page(width=200, height=200)
    pdf_bytes = doc.tobytes()
    doc.close()
    png = ocr.pdf_to_png(pdf_bytes, dpi=72)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
