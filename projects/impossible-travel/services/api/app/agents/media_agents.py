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

"""Визуальные и аудио агенты."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent
from app.models.assets import Asset
from app.models.enums import AssetType
from app.providers.base import GeneratedAsset


class CharacterBibleAgent(BaseAgent):
    name = "character_bible"

    async def run(self, characters: list) -> dict:
        return {"cast": [c.bible if hasattr(c, "bible") else c for c in characters]}


class ImageGenerationAgent(BaseAgent):
    name = "image_generation"

    async def run(
        self,
        session: AsyncSession,
        episode_id: UUID,
        shots: list,
    ) -> list[Asset]:
        assets = []
        for shot in shots:
            gen: GeneratedAsset = await self.providers.image.generate_image(
                shot.get("visual_prompt", ""),
                shot.get("negative_prompt", ""),
                {"episode_id": str(episode_id), "shot_id": shot.get("shot_id", "img")},
            )
            asset = Asset(
                episode_id=episode_id,
                asset_type=AssetType.IMAGE.value,
                storage_key=gen.storage_key,
                url=gen.url,
                meta=gen.meta,
            )
            session.add(asset)
            assets.append(asset)
        return assets


class VideoGenerationAgent(BaseAgent):
    name = "video_generation"

    async def run(
        self,
        session: AsyncSession,
        episode_id: UUID,
        shots: list,
    ) -> list[Asset]:
        assets = []
        for shot in shots:
            gen = await self.providers.video.text_to_video(
                shot.get("visual_prompt", ""),
                {"episode_id": str(episode_id), "shot_id": shot.get("shot_id", "vid")},
            )
            asset = Asset(
                episode_id=episode_id,
                asset_type=AssetType.VIDEO.value,
                storage_key=gen.storage_key,
                url=gen.url,
                meta=gen.meta,
            )
            session.add(asset)
            assets.append(asset)
        return assets


class VoiceoverAgent(BaseAgent):
    name = "voiceover"

    async def run(self, session: AsyncSession, episode_id: UUID, script: str) -> Asset:
        gen = await self.providers.audio.text_to_speech(
            script[:500],
            "mira_ru",
            {"episode_id": str(episode_id)},
        )
        asset = Asset(
            episode_id=episode_id,
            asset_type=AssetType.AUDIO.value,
            storage_key=gen.storage_key,
            url=gen.url,
            meta={**gen.meta, "subtype": "voiceover"},
        )
        session.add(asset)
        return asset


class MusicComposerAgent(BaseAgent):
    name = "music"

    async def run(self, session: AsyncSession, episode_id: UUID, topic: str) -> Asset:
        gen = await self.providers.audio.generate_music(
            f"cinematic ambient sci-fi for {topic}",
            {"episode_id": str(episode_id)},
        )
        asset = Asset(
            episode_id=episode_id,
            asset_type=AssetType.AUDIO.value,
            storage_key=gen.storage_key,
            url=gen.url,
            meta={**gen.meta, "subtype": "music"},
        )
        session.add(asset)
        return asset


class SFXAgent(BaseAgent):
    name = "sfx"

    async def run(self, session: AsyncSession, episode_id: UUID, topic: str) -> Asset:
        gen = await self.providers.audio.generate_sfx(
            f"wind, radio, suit creak for {topic}",
            {"episode_id": str(episode_id)},
        )
        asset = Asset(
            episode_id=episode_id,
            asset_type=AssetType.AUDIO.value,
            storage_key=gen.storage_key,
            url=gen.url,
            meta={**gen.meta, "subtype": "sfx"},
        )
        session.add(asset)
        return asset


class MemoryArchivistAgent(BaseAgent):
    name = "memory_archivist"

    async def run(self, episode_data: dict) -> dict:
        return {
            "archived_prompts": episode_data.get("shotlist", []),
            "location": episode_data.get("location"),
            "learnings": ["mock pipeline completed"],
        }
