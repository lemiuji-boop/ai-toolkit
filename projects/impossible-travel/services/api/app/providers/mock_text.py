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

"""Mock текстовый провайдер."""

import hashlib
import json
import re

from app.constants import AI_DISCLOSURE_EN, AI_DISCLOSURE_RU, DISCLOSURE_TEXT
from app.providers.base import TextProvider


class MockTextProvider(TextProvider):
    """Детерминированные ответы без внешнего API."""

    async def generate_json(
        self, system_prompt: str, user_prompt: str, schema: dict | None = None
    ) -> dict:
        """Возвращает mock JSON по ключевым словам в промпте."""
        topic = _extract_topic(user_prompt)
        lower = (system_prompt + user_prompt).lower()

        if "compliance" in lower or "безопасност" in lower:
            return {
                "decision": "approve",
                "impossible_location_marked": True,
                "disclosure_present": True,
                "disclosure_text": DISCLOSURE_TEXT,
                "issues": [],
            }

        if "idea" in lower or "иде" in lower:
            return {
                "title": f"Я исследовала: {topic}",
                "hook": "Внизу был не огонь. Там был город." if "вулкан" in topic.lower() else f"Здесь {topic} меняет все правила.",
                "location": topic,
                "main_conflict": "дрон обнаружил нечто невозможное",
                "visual_promise": "кинематографичный свет, пыль, отражения, handheld камера",
            }

        if "location" in lower or "локац" in lower:
            return {
                "location_name": f"The Impossible Shore of {topic.title()}",
                "type": "impossible place",
                "danger_level": 8,
                "visual_features": ["dramatic sky", "particles", "cinematic scale"],
                "story_hook": f"В {topic} каждая секунда стоит риска.",
            }

        if "world" in lower or "мир" in lower:
            return {
                "transport": "experimental fold-space travel capsule",
                "survival_system": "reflective thermal suit",
                "camera_system": "autonomous spherical drone",
                "return_condition": "leave before radiation storm",
            }

        if "science" in lower or "правдоподоб" in lower:
            return {
                "plausible": True,
                "notes": "Художественные допущения для выживания героини.",
                "artistic_license": ["protective suit", "stabilized gravity field"],
            }

        if "architect" in lower or "структур" in lower:
            return {
                "segments": [
                    {"range": "0-3", "label": "hook"},
                    {"range": "3-10", "label": "place"},
                    {"range": "10-25", "label": "arrival"},
                    {"range": "25-45", "label": "discovery"},
                    {"range": "45-55", "label": "danger"},
                    {"range": "55-60", "label": "finale"},
                ]
            }

        if "shot" in lower or "раскадр" in lower:
            return {
                "shots": [
                    {
                        "shot_id": "s_001",
                        "duration": 5,
                        "camera": "handheld close-up",
                        "subject": "Mira in reflective helmet",
                        "location": topic,
                        "visual_prompt": f"Vertical 9:16 photorealistic cinematic travel vlog, Mira near {topic}",
                        "negative_prompt": "cartoon, anime, plastic skin, extra fingers",
                    },
                    {
                        "shot_id": "s_002",
                        "duration": 6,
                        "camera": "wide establishing",
                        "subject": "impossible landscape",
                        "location": topic,
                        "visual_prompt": f"Cinematic wide shot of impossible {topic}, documentary style",
                        "negative_prompt": "cartoon, low detail",
                    },
                    {
                        "shot_id": "s_003",
                        "duration": 5,
                        "camera": "medium close-up",
                        "subject": "Mira speaking to camera",
                        "location": topic,
                        "visual_prompt": f"Mira fictional travel vlogger in {topic}, natural skin texture",
                        "negative_prompt": "celebrity likeness, deformed hands",
                    },
                ]
            }

        if "social" in lower or "packaging" in lower:
            return {
                "titles": [
                    f"Я побывала в {topic}",
                    f"Невозможная экспедиция: {topic}",
                    f"Мира: {topic}",
                ],
                "descriptions": [
                    f"Виртуальная экспедиция в {topic}. {AI_DISCLOSURE_RU}",
                    f"AI travel vlog — {topic}. {AI_DISCLOSURE_EN}",
                ],
                "hashtags": ["#AItravel", "#ImpossiblePlaces", "#VirtualExpedition", "#Mira"],
            }

        return {"mock": True, "topic": topic}

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """Генерирует markdown-сценарий."""
        topic = _extract_topic(user_prompt)
        return f"""## Episode Script — {topic}

### 00:00–00:03
Visual: Close-up of Mira's helmet reflecting impossible light.
Voice: «Я думала, что тишина здесь — это красиво. Пока не услышала, как трещит мой скафандр.»
Sound: low rumble, heartbeat, radio noise.

### 00:03–00:10
Visual: Wide shot of {topic}, particles in air.
Voice: «Добро пожаловать в место, куда обычный турист не попадёт.»
Sound: wind, drone hum.

### 00:10–00:25
Visual: Mira steps forward, handheld camera.
Voice: «Меня зовут Мира. Это виртуальная экспедиция — и да, всё, что вы видите, создано ИИ.»
Sound: suit creak, breathing.

### 00:25–00:45
Visual: Discovery — strange structure or phenomenon.
Voice: «Смотрите внимательно. Это не закат. Это что-то другое.»
Sound: tension drone.

### 00:45–00:55
Visual: Danger beat — light flares, alarm.
Voice: «Если сигнал станет красным — мы уже опоздали.»
Sound: alert beep.

### 00:55–01:00
Visual: Mira smiles ironically to camera.
Voice: «Самый красивый вид в моей жизни — и он пытается меня испарить. До встречи в следующем невозможном месте.»
Sound: music swell.

---
{AI_DISCLOSURE_RU}
{AI_DISCLOSURE_EN}
"""


def _extract_topic(user_prompt: str) -> str:
    """Извлекает тему из user prompt."""
    match = re.search(r"topic[:\s]+(.+?)(?:\n|$)", user_prompt, re.I)
    if match:
        return match.group(1).strip()[:120]
    match = re.search(r"тема[:\s]+(.+?)(?:\n|$)", user_prompt, re.I)
    if match:
        return match.group(1).strip()[:120]
    return user_prompt.strip()[:80] or "невозможное место"
