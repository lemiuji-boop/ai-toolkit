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

"""Контракт безопасности (ТЗ §3)."""

from pydantic import BaseModel, Field


class SafetyShieldPayload(BaseModel):
    """Результат проверки guardrail-слоя."""

    is_safe_to_export: bool = Field(
        ...,
        description="False при критических утечках чувствительных данных.",
    )
    detected_violations: list[str] = Field(
        default_factory=list,
        description="Список нарушений категорий правил.",
    )
    sanitized_prompt: str = Field(
        ...,
        description="Промпт без credentials, ID и токсичных инъекций.",
    )
    encryption_required: bool = Field(
        default=False,
        description="True если payload содержит финансовую информацию.",
    )
    hard_blocked: bool = Field(
        default=False,
        description="True при обнаружении credentials — выполнение прервано.",
    )
