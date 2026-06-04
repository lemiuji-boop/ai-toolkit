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

"""Load models.yaml and task suites into the database."""
from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bench.tasks.base import discover_suite_files, load_suite_yaml
from core.models import Fits6Gb, Modality, Model, Task, TaskSuite

BENCH_ROOT = Path(__file__).parent


async def sync_models(session: AsyncSession) -> int:
    """Upsert models from models.yaml. Returns count synced."""
    path = BENCH_ROOT / "models.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    count = 0
    for row in data.get("models", []):
        tag = row["ollama_tag"]
        result = await session.execute(select(Model).where(Model.ollama_tag == tag))
        model = result.scalar_one_or_none()
        fits_raw = row["fits_6gb"]
        if isinstance(fits_raw, bool):
            fits_raw = "yes" if fits_raw else "no"
        fits = Fits6Gb(str(fits_raw))
        modality = Modality(row.get("modality", "text"))
        if model is None:
            model = Model(
                name=row["name"],
                ollama_tag=tag,
                params_b=float(row["params_b"]),
                quant=row.get("quant", "Q4_K_M"),
                family=row["family"],
                est_vram_gb=float(row["est_vram_gb"]),
                fits_6gb=fits,
                context_max=int(row.get("context_max", 8192)),
                modality=modality,
                license=row.get("license", ""),
                notes=row.get("notes"),
            )
            session.add(model)
        else:
            model.name = row["name"]
            model.est_vram_gb = float(row["est_vram_gb"])
            model.fits_6gb = fits
        count += 1
    await session.flush()
    return count


async def sync_task_suites(session: AsyncSession) -> int:
    """Load all YAML task suites into DB."""
    count = 0
    for path in discover_suite_files():
        suite_def = load_suite_yaml(path)
        result = await session.execute(
            select(TaskSuite).where(TaskSuite.name == suite_def.name)
        )
        suite = result.scalar_one_or_none()
        if suite is None:
            suite = TaskSuite(
                name=suite_def.name,
                category=suite_def.category,
                language=suite_def.language,
                description=suite_def.description,
            )
            session.add(suite)
            await session.flush()
        for tdef in suite_def.tasks:
            tres = await session.execute(
                select(Task).where(Task.suite_id == suite.id, Task.key == tdef.key)
            )
            task = tres.scalar_one_or_none()
            if task is None:
                task = Task(
                    suite_id=suite.id,
                    key=tdef.key,
                    prompt=tdef.prompt,
                    system_prompt=tdef.system_prompt,
                    expected=tdef.expected,
                    scorer=tdef.scorer,
                    scorer_config=tdef.scorer_config or {},
                    max_tokens=tdef.max_tokens,
                    weight=tdef.weight,
                )
                session.add(task)
            count += 1
    await session.flush()
    return count
