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

"""Начальные данные: проект, бренд, Мира."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.characters import Character
from app.models.projects import BrandProfile, Project

MIRA_BIBLE = {
    "id": "main_girl",
    "name": "Mira",
    "role": "virtual travel host",
    "age_range": "22-32",
    "personality": "curious, brave, ironic, emotionally honest",
    "visual_traits": {
        "face": "fictional, not based on a real person",
        "hair": "dark blonde medium hair",
        "clothes": "adaptive cinematic travel suit",
        "signature_item": "small silver spherical camera drone",
    },
    "voice": {
        "language": "ru",
        "tone": "warm, natural, expressive",
        "speed": "medium",
    },
    "forbidden": [
        "celebrity likeness",
        "real person clone",
        "licensed character likeness",
        "unstable face between episodes",
    ],
}

BRAND_CONTENT_PILLARS = [
    "impossible nature",
    "space travel",
    "dangerous worlds",
    "lost civilizations",
    "science fantasy",
    "emotional virtual travel",
]


async def seed_database(session: AsyncSession) -> None:
    """Создаёт default project, brand и Mira если их ещё нет."""
    result = await session.execute(select(Project).limit(1))
    project = result.scalar_one_or_none()

    char_result = await session.execute(
        select(Character).where(Character.external_id == "main_girl")
    )
    if char_result.scalar_one_or_none():
        return

    if not project:
        project = Project(
            id=uuid.uuid4(),
            name="Impossible Travel AI",
            description="Виртуальные экспедиции в невозможные места",
        )
        session.add(project)
        await session.flush()

        brand = BrandProfile(
            project_id=project.id,
            brand_voice="cinematic, emotional, curious, slightly ironic",
            visual_identity="photorealistic documentary vlog with cinematic scale",
            content_pillars=BRAND_CONTENT_PILLARS,
        )
        session.add(brand)

    mira = Character(
        project_id=project.id,
        external_id="main_girl",
        name="Mira",
        role="virtual travel host",
        bible=MIRA_BIBLE,
    )
    session.add(mira)
    await session.commit()
