"""OCR-препроцессор (FR-002).

Готовит изображение чертежа к подаче в VLM:
1) растеризует одностраничный PDF в PNG (PyMuPDF);
2) локализует ключевые зоны — основную надпись и поле спецификации.

Локализация здесь — геометрическая эвристика по ГОСТ 2.104 (основная надпись в
правом нижнем углу листа). Это даёт стабильные debug-координаты без тяжёлого OCR.
Полноценная локализация (PaddleOCR/Surya) подключается позже без изменения
сигнатур функций этого модуля.
"""
from __future__ import annotations

from typing import Any

from app.core.config import settings


def is_pdf(data: bytes) -> bool:
    """Является ли вход PDF (по сигнатуре файла)."""
    return data[:5] == b"%PDF-"


def pdf_to_png(data: bytes, dpi: int | None = None) -> bytes:
    """Первая страница PDF → PNG. При ошибке/недоступности PyMuPDF возвращает вход как есть."""
    used_dpi = dpi or settings.image_dpi
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=data, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=used_dpi)
        png = pix.tobytes("png")
        doc.close()
        return png
    except Exception:
        # Не PDF или PyMuPDF недоступен — отдаём исходные байты (растровый чертёж).
        return data


def locate_zones(_image: bytes) -> dict[str, list[float]]:
    """Относительные координаты зон [x0, y0, x1, y1] в долях стороны [0..1].

    Основная надпись — правый нижний угол (ГОСТ 2.104), спецификация — над ней.
    """
    return {
        "title_block": [0.62, 0.86, 1.0, 1.0],
        "specification": [0.62, 0.55, 1.0, 0.86],
    }


def preprocess(data: bytes) -> tuple[bytes, dict[str, Any]]:
    """Подготовка к VLM: PDF→PNG + локализация зон.

    Возвращает кортеж (png_bytes, debug), где debug содержит координаты зон и
    признак исходного формата. Если OCR отключён — зоны пустые.
    """
    was_pdf = is_pdf(data)
    png = pdf_to_png(data) if was_pdf else data
    zones = locate_zones(png) if settings.ocr_enabled else {}
    debug: dict[str, Any] = {"source_was_pdf": was_pdf, "zones": zones}
    return png, debug
