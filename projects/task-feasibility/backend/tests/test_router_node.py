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

"""Тесты router_node."""

from app.agents.nodes.router import router_node


def test_l2_crud() -> None:
    state = {
        "user_task": "Создать CRUD endpoints для заказов",
        "project_name": "Shop",
        "context_lines": 0,
    }
    out = router_node(state)  # type: ignore[arg-type]
    assert out["complexity_level"] == "L2"


def test_l4_architect() -> None:
    state = {
        "user_task": "Спроектировать creative system architect from scratch",
        "project_name": "X",
        "context_lines": 0,
    }
    out = router_node(state)  # type: ignore[arg-type]
    assert out["complexity_level"] == "L4"
