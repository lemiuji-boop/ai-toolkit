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

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class OcrPageResult:
    text: str
    confidence: float
    method: str = "tesseract"


class OcrProvider(ABC):
    @abstractmethod
    def recognize_page(self, image: bytes) -> OcrPageResult: ...


class TesseractProvider(OcrProvider):
    def recognize_page(self, image: bytes) -> OcrPageResult:
        try:
            import pytesseract
            from PIL import Image
            from io import BytesIO

            img = Image.open(BytesIO(image))
            text = pytesseract.image_to_string(img, lang="rus+eng")
            return OcrPageResult(text=text, confidence=0.65, method="tesseract")
        except Exception:
            return OcrPageResult(text="", confidence=0.0, method="tesseract")


class PaddleOcrProvider(OcrProvider):
    """COULD: полная интеграция PaddleOCR (GPU)."""

    def recognize_page(self, image: bytes) -> OcrPageResult:
        return OcrPageResult(text="", confidence=0.0, method="paddle_stub")


def get_ocr_provider() -> OcrProvider:
    """Фабрика OCR по OCR_PROVIDER в .env."""
    from app.core.config import settings

    if settings.ocr_provider.lower() == "paddle":
        return PaddleOcrProvider()
    return TesseractProvider()
