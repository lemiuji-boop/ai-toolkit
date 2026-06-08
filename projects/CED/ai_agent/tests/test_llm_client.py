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

"""Тесты llm_client с mock Ollama."""

from unittest.mock import MagicMock, patch

from app.services import llm_client


def test_ollama_available_ok() -> None:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    with patch("app.services.llm_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.return_value = mock_resp
        with patch("app.services.llm_client.resolve_ollama_base_url", return_value="http://127.0.0.1:11434"):
            assert llm_client.ollama_available() is True


def test_ollama_available_fail() -> None:
    with patch("app.services.llm_client.httpx.Client") as client_cls:
        client_cls.return_value.__enter__.return_value.get.side_effect = OSError("down")
        with patch("app.services.llm_client.resolve_ollama_base_url", return_value="http://127.0.0.1:11434"):
            assert llm_client.ollama_available() is False


def test_enrich_skips_when_ollama_down() -> None:
    fields = {"name": {"value": "", "confidence": 0.0}}
    with patch("app.services.llm_client.ollama_available", return_value=False):
        result = llm_client.enrich_kd_fields_with_llm(fields, "text")
    assert result == fields
