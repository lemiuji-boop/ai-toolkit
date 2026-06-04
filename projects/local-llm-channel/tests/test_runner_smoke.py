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

"""Runner smoke — requires Ollama; skipped if unavailable."""
from __future__ import annotations

import pytest

from bench.ollama_client import OllamaClient


@pytest.mark.asyncio
async def test_ollama_health() -> None:
    client = OllamaClient()
    ok = await client.health()
    if not ok:
        pytest.skip("Ollama not running")
    assert ok
