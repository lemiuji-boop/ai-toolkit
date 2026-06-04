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

"""Провайдеры LLM."""

from app.llm.providers.base import ChatMessage, LLMProvider, LLMResponse
from app.llm.providers.ollama import OllamaProvider
from app.llm.providers.openai_compat import OpenAICompatibleProvider

__all__ = [
    "ChatMessage",
    "LLMProvider",
    "LLMResponse",
    "OllamaProvider",
    "OpenAICompatibleProvider",
]
