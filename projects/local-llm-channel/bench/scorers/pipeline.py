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

"""Score all runs in an experiment."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bench.scorers.judge import judge_output
from bench.scorers.rule_based import score_run
from core.models import Experiment, Run, Score, ScorerType


async def score_experiment(session: AsyncSession, experiment_id: int) -> int:
    """Score every run; returns count scored."""
    exp = await session.get(Experiment, experiment_id)
    if exp is None:
        raise ValueError(f"Experiment {experiment_id} not found")

    result = await session.execute(
        select(Run)
        .where(Run.experiment_id == experiment_id)
        .options(selectinload(Run.task), selectinload(Run.scores))
    )
    runs = list(result.scalars().all())

    count = 0
    for run in runs:
        if not run.output_text:
            continue
        if run.scores:
            continue
        task = run.task
        value: float = 0.0
        raw: dict[str, object] = {}
        rationale: str | None = None
        if task.scorer == ScorerType.judge:
            value, raw, rationale = await judge_output(task.prompt, run.output_text)
        else:
            value, raw = score_run(
                run.output_text,
                task.scorer,
                task.expected,
                task.scorer_config or {},
            )
        session.add(
            Score(
                run_id=run.id,
                scorer=task.scorer.value,
                value=value,
                raw=raw,
                rationale=rationale,
            )
        )
        count += 1
    await session.flush()
    return count
