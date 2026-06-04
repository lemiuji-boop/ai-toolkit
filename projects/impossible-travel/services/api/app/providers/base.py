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

"""Абстракции AI-провайдеров."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class GeneratedAsset:
    """Результат генерации медиа."""

    storage_key: str
    url: str
    mime_type: str
    meta: dict[str, Any]


class TextProvider(ABC):
    """Текстовый провайдер."""

    @abstractmethod
    async def generate_json(
        self, system_prompt: str, user_prompt: str, schema: dict | None = None
    ) -> dict:
        pass

    @abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        pass


class ImageProvider(ABC):
    """Генерация изображений."""

    @abstractmethod
    async def generate_image(
        self, prompt: str, negative_prompt: str, params: dict | None = None
    ) -> GeneratedAsset:
        pass


class VideoProvider(ABC):
    """Генерация видео."""

    @abstractmethod
    async def text_to_video(self, prompt: str, params: dict | None = None) -> GeneratedAsset:
        pass

    @abstractmethod
    async def image_to_video(
        self, image_url: str, prompt: str, params: dict | None = None
    ) -> GeneratedAsset:
        pass


class AudioProvider(ABC):
    """Озвучка и звук."""

    @abstractmethod
    async def text_to_speech(
        self, text: str, voice_id: str, params: dict | None = None
    ) -> GeneratedAsset:
        pass

    @abstractmethod
    async def generate_music(self, prompt: str, params: dict | None = None) -> GeneratedAsset:
        pass

    @abstractmethod
    async def generate_sfx(self, prompt: str, params: dict | None = None) -> GeneratedAsset:
        pass


@dataclass
class ProviderBundle:
    """Набор провайдеров для пайплайна."""

    text: TextProvider
    image: ImageProvider
    video: VideoProvider
    audio: AudioProvider
