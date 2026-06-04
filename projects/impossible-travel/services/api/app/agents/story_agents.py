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

"""Сценарные и мировые агенты."""

from app.agents.base import BaseAgent
from app.constants import DISCLOSURE_TEXT, NEGATIVE_PROMPT_DEFAULT


class EpisodeIdeaAgent(BaseAgent):
    name = "episode_idea"

    async def run(self, topic: str) -> dict:
        return await self.text.generate_json(
            "Episode idea agent",
            f"Generate episode idea for topic: {topic}",
        )


class ImpossibleLocationAgent(BaseAgent):
    name = "impossible_location"

    async def run(self, topic: str, idea: dict) -> dict:
        return await self.text.generate_json(
            "Impossible location agent",
            f"Create impossible location for topic: {topic}. Idea: {idea}",
        )


class WorldbuildingAgent(BaseAgent):
    name = "worldbuilding"

    async def run(self, topic: str, location: dict) -> dict:
        return await self.text.generate_json(
            "Worldbuilding agent",
            f"World rules for topic: {topic}. Location: {location}",
        )


class SciencePlausibilityAgent(BaseAgent):
    name = "science_plausibility"

    async def run(self, topic: str, world: dict) -> dict:
        return await self.text.generate_json(
            "Science plausibility agent",
            f"Validate plausibility for: {topic}. World: {world}",
        )


class EpisodeArchitectAgent(BaseAgent):
    name = "episode_architect"

    async def run(self, topic: str, duration: int) -> dict:
        return await self.text.generate_json(
            "Episode architect — structure with timecodes",
            f"Structure episode {duration}s for topic: {topic}",
        )


class ScriptWriterAgent(BaseAgent):
    name = "script_writer"

    async def run(self, topic: str, idea: dict, architect: dict) -> str:
        return await self.text.generate_text(
            "Script writer — photorealistic AI travel vlog",
            f"Write script. topic: {topic}. idea: {idea}. structure: {architect}",
        )


class DialogueAgent(BaseAgent):
    name = "dialogue"

    async def run(self, script: str) -> str:
        # MVP: лёгкая полировка — возвращаем тот же сценарий
        return script


class ShotlistAgent(BaseAgent):
    name = "shotlist"

    async def run(self, topic: str, script: str) -> list:
        data = await self.text.generate_json(
            "Shotlist agent",
            f"Create shotlist for topic: {topic}. Script excerpt: {script[:500]}",
        )
        return data.get("shots", [])


class VisualDirectorAgent(BaseAgent):
    name = "visual_director"

    async def run(self, topic: str) -> dict:
        return {
            "style": "photorealistic documentary vlog",
            "camera": "handheld, natural shake, 35mm lens",
            "lighting": "dramatic but believable",
            "realism": ["dust", "lens flare", "heat haze", "skin texture"],
            "topic": topic,
        }


class PromptEngineerAgent(BaseAgent):
    name = "prompt_engineer"

    async def run(self, shots: list) -> list:
        """Дополняет negative prompt если отсутствует."""
        enriched = []
        for shot in shots:
            s = dict(shot)
            s.setdefault("negative_prompt", NEGATIVE_PROMPT_DEFAULT)
            enriched.append(s)
        return enriched


class SocialPackagingAgent(BaseAgent):
    name = "social_packaging"

    async def run(self, topic: str, idea: dict) -> dict:
        data = await self.text.generate_json(
            "Social packaging agent",
            f"Create social package for topic: {topic}. idea: {idea}",
        )
        platforms = {
            "instagram": {
                "caption": data.get("descriptions", [""])[0],
                "hashtags": data.get("hashtags", []),
            },
            "tiktok": {
                "caption": data.get("descriptions", ["", ""])[-1],
                "hashtags": data.get("hashtags", []),
            },
            "youtube_shorts": {
                "title": data.get("titles", [topic])[0],
                "description": data.get("descriptions", [""])[0],
            },
            "pinterest": {"title": data.get("titles", [topic])[0]},
            "telegram": {"text": data.get("descriptions", [""])[0]},
            "website": {"title": data.get("titles", [topic])[0], "body": data.get("descriptions", [""])[0]},
        }
        return {
            "titles": data.get("titles", []),
            "descriptions": data.get("descriptions", []),
            "hashtags": data.get("hashtags", []),
            "disclosure": DISCLOSURE_TEXT,
            "platforms": platforms,
            "behind_the_scenes": f"Как создавалась виртуальная экспедиция: {topic}",
        }


class ComplianceAgent(BaseAgent):
    name = "compliance"

    async def run(self, topic: str, packages: dict) -> dict:
        result = await self.text.generate_json(
            "Compliance agent — safety and AI disclosure",
            f"Check compliance for topic: {topic}. packages: {packages}",
        )
        disclosure = packages.get("disclosure", DISCLOSURE_TEXT)
        result["disclosure_text"] = disclosure
        if not result.get("disclosure_present"):
            result["decision"] = "reject"
            result["issues"] = result.get("issues", []) + ["missing_disclosure"]
        return result
