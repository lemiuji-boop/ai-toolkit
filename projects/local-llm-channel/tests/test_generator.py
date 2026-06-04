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

"""Content generator tests."""
from __future__ import annotations

from content.render import enforce_telegram_limits, render_template


def test_telegram_limit() -> None:
    long = "x" * 5000
    short = enforce_telegram_limits(long)
    assert len(short) <= 4096


def test_render_template() -> None:
    body = render_template(
        "fits_6gb.md.j2",
        title="Test",
        rows=[],
        hardware="RTX 3060",
        methodology="3x",
    )
    assert "6 ГБ" in body or "Test" in body
