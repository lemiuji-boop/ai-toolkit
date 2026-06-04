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

"""Пайплайн генерации выпуска."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.media_agents import (
    CharacterBibleAgent,
    ImageGenerationAgent,
    MemoryArchivistAgent,
    MusicComposerAgent,
    SFXAgent,
    VideoGenerationAgent,
    VoiceoverAgent,
)
from app.agents.story_agents import (
    ComplianceAgent,
    DialogueAgent,
    EpisodeArchitectAgent,
    EpisodeIdeaAgent,
    ImpossibleLocationAgent,
    PromptEngineerAgent,
    SciencePlausibilityAgent,
    ScriptWriterAgent,
    ShotlistAgent,
    SocialPackagingAgent,
    VisualDirectorAgent,
    WorldbuildingAgent,
)
from app.constants import DISCLOSURE_TEXT
from app.models.characters import Character
from app.models.enums import EpisodeStatus, GenerationTaskStatus
from app.models.episodes import Episode, Shot
from app.models.locations import Location
from app.models.projects import Project
from app.models.tasks import GenerationTask
from app.providers.factory import get_providers

logger = logging.getLogger(__name__)

PIPELINE_STEPS = [
    "episode_idea",
    "impossible_location",
    "worldbuilding",
    "science_plausibility",
    "character_bible",
    "episode_architect",
    "script_writer",
    "dialogue",
    "shotlist",
    "visual_director",
    "prompt_engineer",
    "image_generation",
    "video_generation",
    "voiceover",
    "music",
    "sfx",
    "social_packaging",
    "compliance",
    "quality_gates",
    "memory_archivist",
]


class EpisodePipeline:
    """Chief orchestrator — полный цикл генерации."""

    def __init__(self) -> None:
        self.providers = get_providers()

    async def _update_task(
        self,
        session: AsyncSession,
        episode_id: UUID,
        step: str,
        status: GenerationTaskStatus,
        progress: float,
        error: str | None = None,
    ) -> None:
        result = await session.execute(
            select(GenerationTask).where(
                GenerationTask.episode_id == episode_id,
                GenerationTask.step == step,
            )
        )
        task = result.scalar_one_or_none()
        if not task:
            task = GenerationTask(episode_id=episode_id, step=step)
            session.add(task)
        task.status = status.value if hasattr(status, "value") else status
        task.progress = progress
        task.error = error
        await session.flush()

    async def run(self, session: AsyncSession, episode_id: UUID) -> None:
        """Запускает полный пайплайн."""
        episode = await session.get(Episode, episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found")

        episode.status = EpisodeStatus.GENERATING.value
        await session.commit()

        try:
            total = len(PIPELINE_STEPS)
            topic = episode.topic

            # Инициализация задач
            for i, step in enumerate(PIPELINE_STEPS):
                await self._update_task(
                    session,
                    episode_id,
                    step,
                    GenerationTaskStatus.PENDING,
                    i / total,
                )
            await session.commit()

            idea_agent = EpisodeIdeaAgent(self.providers)
            await self._update_task(session, episode_id, "episode_idea", GenerationTaskStatus.RUNNING, 0.05)
            idea = await idea_agent.run(topic)
            episode.idea = idea
            episode.title = idea.get("title")
            await self._update_task(session, episode_id, "episode_idea", GenerationTaskStatus.DONE, 0.05)
            await session.commit()

            loc_agent = ImpossibleLocationAgent(self.providers)
            await self._update_task(session, episode_id, "impossible_location", GenerationTaskStatus.RUNNING, 0.1)
            loc_data = await loc_agent.run(topic, idea)
            project = await session.get(Project, episode.project_id)
            location = Location(
                project_id=episode.project_id,
                episode_id=episode.id,
                name=loc_data.get("location_name", topic),
                location_type=loc_data.get("type", "impossible"),
                data=loc_data,
            )
            session.add(location)
            await session.flush()
            episode.location_id = location.id
            await self._update_task(session, episode_id, "impossible_location", GenerationTaskStatus.DONE, 0.1)
            await session.commit()

            world_agent = WorldbuildingAgent(self.providers)
            await self._update_task(session, episode_id, "worldbuilding", GenerationTaskStatus.RUNNING, 0.15)
            world = await world_agent.run(topic, loc_data)
            episode.worldbuilding = world
            await self._update_task(session, episode_id, "worldbuilding", GenerationTaskStatus.DONE, 0.15)

            sci_agent = SciencePlausibilityAgent(self.providers)
            await self._update_task(session, episode_id, "science_plausibility", GenerationTaskStatus.RUNNING, 0.2)
            episode.science_check = await sci_agent.run(topic, world)
            await self._update_task(session, episode_id, "science_plausibility", GenerationTaskStatus.DONE, 0.2)

            chars_result = await session.execute(
                select(Character).where(Character.project_id == episode.project_id)
            )
            characters = list(chars_result.scalars().all())
            char_agent = CharacterBibleAgent(self.providers)
            await self._update_task(session, episode_id, "character_bible", GenerationTaskStatus.RUNNING, 0.25)
            cast = await char_agent.run(characters)
            await self._update_task(session, episode_id, "character_bible", GenerationTaskStatus.DONE, 0.25)

            arch_agent = EpisodeArchitectAgent(self.providers)
            await self._update_task(session, episode_id, "episode_architect", GenerationTaskStatus.RUNNING, 0.3)
            architect = await arch_agent.run(topic, episode.duration_target)
            episode.architect = architect
            await self._update_task(session, episode_id, "episode_architect", GenerationTaskStatus.DONE, 0.3)

            script_agent = ScriptWriterAgent(self.providers)
            await self._update_task(session, episode_id, "script_writer", GenerationTaskStatus.RUNNING, 0.35)
            script = await script_agent.run(topic, idea, architect)
            await self._update_task(session, episode_id, "script_writer", GenerationTaskStatus.DONE, 0.35)

            dlg_agent = DialogueAgent(self.providers)
            await self._update_task(session, episode_id, "dialogue", GenerationTaskStatus.RUNNING, 0.4)
            script = await dlg_agent.run(script)
            episode.script = script
            await self._update_task(session, episode_id, "dialogue", GenerationTaskStatus.DONE, 0.4)

            shot_agent = ShotlistAgent(self.providers)
            await self._update_task(session, episode_id, "shotlist", GenerationTaskStatus.RUNNING, 0.45)
            shots = await shot_agent.run(topic, script)
            await self._update_task(session, episode_id, "shotlist", GenerationTaskStatus.DONE, 0.45)

            vis_agent = VisualDirectorAgent(self.providers)
            await self._update_task(session, episode_id, "visual_director", GenerationTaskStatus.RUNNING, 0.5)
            episode.visual_style = await vis_agent.run(topic)
            await self._update_task(session, episode_id, "visual_director", GenerationTaskStatus.DONE, 0.5)

            prompt_agent = PromptEngineerAgent(self.providers)
            await self._update_task(session, episode_id, "prompt_engineer", GenerationTaskStatus.RUNNING, 0.55)
            shots = await prompt_agent.run(shots)
            episode.shotlist = shots
            # Сохраняем Shot rows
            for idx, s in enumerate(shots):
                shot_row = Shot(
                    episode_id=episode.id,
                    shot_external_id=s.get("shot_id", f"s_{idx:03d}"),
                    duration=s.get("duration", 5),
                    camera=s.get("camera"),
                    subject=s.get("subject"),
                    location_text=s.get("location"),
                    visual_prompt=s.get("visual_prompt"),
                    negative_prompt=s.get("negative_prompt"),
                    order_index=idx,
                )
                session.add(shot_row)
            await self._update_task(session, episode_id, "prompt_engineer", GenerationTaskStatus.DONE, 0.55)
            await session.commit()

            img_agent = ImageGenerationAgent(self.providers)
            await self._update_task(session, episode_id, "image_generation", GenerationTaskStatus.RUNNING, 0.65)
            await img_agent.run(session, episode_id, shots)
            await self._update_task(session, episode_id, "image_generation", GenerationTaskStatus.DONE, 0.65)

            vid_agent = VideoGenerationAgent(self.providers)
            await self._update_task(session, episode_id, "video_generation", GenerationTaskStatus.RUNNING, 0.75)
            await vid_agent.run(session, episode_id, shots)
            await self._update_task(session, episode_id, "video_generation", GenerationTaskStatus.DONE, 0.75)

            vo_agent = VoiceoverAgent(self.providers)
            await self._update_task(session, episode_id, "voiceover", GenerationTaskStatus.RUNNING, 0.8)
            await vo_agent.run(session, episode_id, script)
            await self._update_task(session, episode_id, "voiceover", GenerationTaskStatus.DONE, 0.8)

            music_agent = MusicComposerAgent(self.providers)
            await self._update_task(session, episode_id, "music", GenerationTaskStatus.RUNNING, 0.85)
            await music_agent.run(session, episode_id, topic)
            await self._update_task(session, episode_id, "music", GenerationTaskStatus.DONE, 0.85)

            sfx_agent = SFXAgent(self.providers)
            await self._update_task(session, episode_id, "sfx", GenerationTaskStatus.RUNNING, 0.9)
            await sfx_agent.run(session, episode_id, topic)
            await self._update_task(session, episode_id, "sfx", GenerationTaskStatus.DONE, 0.9)
            await session.commit()

            social_agent = SocialPackagingAgent(self.providers)
            await self._update_task(session, episode_id, "social_packaging", GenerationTaskStatus.RUNNING, 0.92)
            packages = await social_agent.run(topic, idea)
            episode.platform_packages = packages
            await self._update_task(session, episode_id, "social_packaging", GenerationTaskStatus.DONE, 0.92)

            compliance_agent = ComplianceAgent(self.providers)
            await self._update_task(session, episode_id, "compliance", GenerationTaskStatus.RUNNING, 0.95)
            compliance = await compliance_agent.run(topic, packages)
            episode.compliance_report = compliance
            await self._update_task(session, episode_id, "compliance", GenerationTaskStatus.DONE, 0.95)

            await self._update_task(session, episode_id, "quality_gates", GenerationTaskStatus.RUNNING, 0.97)
            episode.quality_report = _build_quality_report(idea, compliance)
            await self._update_task(session, episode_id, "quality_gates", GenerationTaskStatus.DONE, 0.97)

            mem_agent = MemoryArchivistAgent(self.providers)
            await self._update_task(session, episode_id, "memory_archivist", GenerationTaskStatus.RUNNING, 0.99)
            episode.episode_metadata = await mem_agent.run(
                {
                    "shotlist": shots,
                    "location": loc_data,
                    "cast": cast,
                }
            )
            await self._update_task(session, episode_id, "memory_archivist", GenerationTaskStatus.DONE, 1.0)

            if compliance.get("decision") == "reject":
                episode.status = EpisodeStatus.FAILED.value
            else:
                episode.status = EpisodeStatus.READY_FOR_REVIEW.value

            await session.commit()
            logger.info("Pipeline completed for episode %s", episode_id)

        except Exception as exc:
            logger.exception("Pipeline failed: %s", exc)
            episode.status = EpisodeStatus.FAILED.value
            await session.commit()
            raise


def _build_quality_report(idea: dict, compliance: dict) -> dict:
    """Quality gates (mock scores)."""
    disclosure_ok = compliance.get("disclosure_present", True)
    return {
        "story": {
            "hook": bool(idea.get("hook")),
            "passed": True,
            "score": 0.9,
        },
        "visual": {"photorealism": True, "passed": True, "score": 0.85},
        "character": {"consistency": True, "passed": True, "score": 0.9},
        "compliance": {
            "disclosure": disclosure_ok,
            "passed": compliance.get("decision") != "reject",
            "score": 1.0 if disclosure_ok else 0.0,
        },
        "overall_passed": compliance.get("decision") != "reject",
    }
