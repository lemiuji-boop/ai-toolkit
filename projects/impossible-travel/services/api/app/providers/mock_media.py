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

"""Mock image/video/audio провайдеры."""

import io
import struct
import wave
from typing import Any

from app.providers.base import AudioProvider, GeneratedAsset, ImageProvider, VideoProvider


class MockImageProvider(ImageProvider):
    """Placeholder PNG через Pillow."""

    def __init__(self, storage) -> None:
        self._storage = storage

    async def generate_image(
        self, prompt: str, negative_prompt: str, params: dict | None = None
    ) -> GeneratedAsset:
        from PIL import Image, ImageDraw

        params = params or {}
        episode_id = params.get("episode_id", "unknown")
        shot_id = params.get("shot_id", "img")
        width = params.get("width", 576)
        height = params.get("height", 1024)

        img = Image.new("RGB", (width, height), color=(30, 35, 50))
        draw = ImageDraw.Draw(img)
        draw.rectangle([40, 40, width - 40, height - 40], outline=(200, 120, 80), width=3)
        draw.text((60, 60), "Mock Frame", fill=(220, 220, 220))
        draw.text((60, 90), prompt[:60] + "...", fill=(180, 180, 180))

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        key = f"generated/{episode_id}/{shot_id}.png"
        url = await self._storage.upload_bytes(key, buf.getvalue(), "image/png")
        return GeneratedAsset(storage_key=key, url=url, mime_type="image/png", meta={"mock": True})


class MockVideoProvider(VideoProvider):
    """Минимальный mock — сохраняем PNG как pseudo-video metadata."""

    def __init__(self, storage) -> None:
        self._storage = storage

    async def text_to_video(self, prompt: str, params: dict | None = None) -> GeneratedAsset:
        params = params or {}
        episode_id = params.get("episode_id", "unknown")
        shot_id = params.get("shot_id", "vid")
        # Минимальный валидный MP4 header stub (ftyp) + placeholder bytes
        data = _minimal_mp4_stub()
        key = f"generated/{episode_id}/{shot_id}.mp4"
        url = await self._storage.upload_bytes(key, data, "video/mp4")
        return GeneratedAsset(
            storage_key=key,
            url=url,
            mime_type="video/mp4",
            meta={"mock": True, "prompt": prompt[:200]},
        )

    async def image_to_video(
        self, image_url: str, prompt: str, params: dict | None = None
    ) -> GeneratedAsset:
        return await self.text_to_video(prompt, params)


class MockAudioProvider(AudioProvider):
    """Silent/minimal WAV."""

    def __init__(self, storage) -> None:
        self._storage = storage

    async def text_to_speech(
        self, text: str, voice_id: str, params: dict | None = None
    ) -> GeneratedAsset:
        return await self._save_wav(params, "voice", {"type": "tts", "voice_id": voice_id})

    async def generate_music(self, prompt: str, params: dict | None = None) -> GeneratedAsset:
        return await self._save_wav(params, "music", {"type": "music", "prompt": prompt[:100]})

    async def generate_sfx(self, prompt: str, params: dict | None = None) -> GeneratedAsset:
        return await self._save_wav(params, "sfx", {"type": "sfx", "prompt": prompt[:100]})

    async def _save_wav(self, params: dict | None, suffix: str, meta: dict) -> GeneratedAsset:
        params = params or {}
        episode_id = params.get("episode_id", "unknown")
        data = _silent_wav(seconds=1)
        key = f"generated/{episode_id}/{suffix}_{meta['type']}.wav"
        url = await self._storage.upload_bytes(key, data, "audio/wav")
        return GeneratedAsset(storage_key=key, url=url, mime_type="audio/wav", meta={"mock": True, **meta})


def _silent_wav(seconds: float = 1.0, rate: int = 22050) -> bytes:
    """Создаёт короткий silent WAV."""
    nframes = int(rate * seconds)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(b"\x00\x00" * nframes)
    return buf.getvalue()


def _minimal_mp4_stub() -> bytes:
    """Минимальные байты для идентификации как mock video."""
    ftyp = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"
    mdat = b"\x00\x00\x00\x08mdat" + b"\x00" * 64
    return ftyp + mdat
