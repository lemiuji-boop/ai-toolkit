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

"""Резолвер активного ИИ-провайдера из backend БД."""

from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class ResolvedProvider:
    name: str
    base_url: str
    model_name: str
    provider_type: str


def get_active_provider() -> ResolvedProvider:
    backend_url = settings.backend_internal_url
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                f"{backend_url}/internal/ai-provider",
                headers={"X-API-Key": settings.api_key},
            )
            if response.status_code == 200:
                data = response.json()
                return ResolvedProvider(
                    name=data.get("name", "ollama-local"),
                    base_url=data.get("base_url", "http://localhost:11434"),
                    model_name=data.get("model_name", "qwen2.5-coder"),
                    provider_type=data.get("provider_type", "local"),
                )
    except Exception:
        pass
    from app.core.config import settings

    return ResolvedProvider(
        name="ollama-local",
        base_url=settings.ollama_base_url,
        model_name="qwen2.5-coder",
        provider_type="local",
    )
