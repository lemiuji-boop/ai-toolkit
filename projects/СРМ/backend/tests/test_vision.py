"""Тесты распознавания (FR-001/002/003/004) — без GPU и без реального LLM."""
import importlib.util
import json

import pytest

from app.services import ocr, vision

_HAS_FITZ = importlib.util.find_spec("fitz") is not None


class _FakeResponse:
    """Подделка ответа Ollama /api/chat для мокинга httpx.post."""

    def __init__(self, content: dict):
        self._content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"message": {"content": json.dumps(self._content, ensure_ascii=False)}}


def _patch_llm(monkeypatch, content: dict) -> None:
    monkeypatch.setattr(vision.httpx, "post", lambda *a, **k: _FakeResponse(content))


def test_extract_llm_success_with_confidence(monkeypatch):
    # Модель вернула полный набор полей и уверенности (FR-001, FR-003).
    _patch_llm(monkeypatch, {
        "designation": "АБВГ.123.456",
        "name": "Нервюра",
        "material": "АМг6",
        "mass_kg": 0.31,
        "dimensions_mm": {"length": 200, "width": 120, "height": 8},
        "confidence": {"designation": 0.95, "material": 0.88},
    })
    res = vision.extract(b"\x89PNG\r\n")
    assert res.source == "llm"
    assert res.material == "АМг6"
    assert res.confidence["designation"] == 0.95
    # Поля без явной уверенности от модели получают порог по умолчанию.
    assert res.confidence["mass_kg"] == vision.settings.conf_threshold
    assert "dimensions_mm" in res.confidence


def test_fr004_unreadable_fields_stay_null(monkeypatch):
    # Нечитаемые поля → null и НЕ попадают в confidence (FR-004).
    _patch_llm(monkeypatch, {
        "designation": "АБВГ.999.000",
        "name": None,
        "material": None,
        "mass_kg": None,
        "dimensions_mm": {"length": None, "width": None, "height": None},
        "confidence": {"designation": 0.9},
    })
    res = vision.extract(b"img")
    assert res.material is None
    assert res.mass_kg is None
    assert "material" not in res.confidence
    assert "mass_kg" not in res.confidence
    assert "dimensions_mm" not in res.confidence
    assert res.confidence["designation"] == 0.9


def test_extract_degrades_to_stub_on_inference_error(monkeypatch):
    # Любая ошибка inference → детерминированная заглушка (NFR-002).
    def _boom(*a, **k):
        raise RuntimeError("inference down")

    monkeypatch.setattr(vision.httpx, "post", _boom)
    res = vision.extract(b"img")
    assert res.source == "stub"
    assert res.material == "Д16"


def test_ocr_preprocess_png_passthrough_and_zones():
    # PNG проходит без растеризации; зоны локализованы (FR-002).
    png, debug = ocr.preprocess(b"\x89PNG\r\n\x1a\n")
    assert debug["source_was_pdf"] is False
    assert "title_block" in debug["zones"]
    assert len(debug["zones"]["title_block"]) == 4


def test_ocr_detects_pdf_signature():
    assert ocr.is_pdf(b"%PDF-1.7\n...") is True
    assert ocr.is_pdf(b"\x89PNG") is False


@pytest.mark.skipif(not _HAS_FITZ, reason="PyMuPDF не установлен")
def test_ocr_pdf_to_png_converts():
    # Минимальный валидный PDF из одной пустой страницы → PNG-байты.
    import fitz

    doc = fitz.open()
    doc.new_page(width=200, height=200)
    pdf_bytes = doc.tobytes()
    doc.close()
    png = ocr.pdf_to_png(pdf_bytes, dpi=72)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
