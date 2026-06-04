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

"""Jinja rendering and Telegram length limits."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.config import get_settings

TG_MESSAGE_MAX = 4096
TG_CAPTION_MAX = 1024

TEMPLATES_DIR = Path(__file__).parent / "templates"


def get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=()),
    )


def render_template(name: str, **ctx: object) -> str:
    env = get_env()
    template = env.get_template(name)
    return template.render(brand=get_settings().brand_name, **ctx)


def enforce_telegram_limits(body: str, *, is_caption: bool = False) -> str:
    """Обрезка текста под лимиты Telegram."""
    limit = TG_CAPTION_MAX if is_caption else TG_MESSAGE_MAX
    if len(body) <= limit:
        return body
    return body[: limit - 20] + "\n\n…(обрезано)"
