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

"""Task and TaskSuite definitions."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from core.models import ScorerType, TaskCategory, TaskLanguage


@dataclass
class TaskDef:
    key: str
    prompt: str
    scorer: ScorerType
    max_tokens: int
    weight: float
    system_prompt: str | None = None
    expected: str | None = None
    scorer_config: dict[str, Any] | None = None


@dataclass
class TaskSuiteDef:
    name: str
    category: TaskCategory
    language: TaskLanguage
    description: str
    tasks: list[TaskDef]


def load_suite_yaml(path: Path) -> TaskSuiteDef:
    """Load a task suite from YAML file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    suite = data["suite"]
    tasks = []
    for t in data.get("tasks", []):
        scorer_name = t.get("scorer", "judge")
        scorer = ScorerType(scorer_name) if scorer_name != "json" else ScorerType.json_scorer
        tasks.append(
            TaskDef(
                key=t["key"],
                prompt=t["prompt"],
                scorer=scorer,
                max_tokens=int(t.get("max_tokens", 256)),
                weight=float(t.get("weight", 1.0)),
                system_prompt=t.get("system_prompt"),
                expected=t.get("expected"),
                scorer_config=t.get("scorer_config"),
            )
        )
    return TaskSuiteDef(
        name=suite["name"],
        category=TaskCategory(suite["category"]),
        language=TaskLanguage(suite["language"]),
        description=suite.get("description", ""),
        tasks=tasks,
    )


def discover_suite_files(tasks_dir: Path | None = None) -> list[Path]:
    """Find all suite YAML files."""
    base = tasks_dir or Path(__file__).parent
    return sorted(base.glob("*.yaml"))
