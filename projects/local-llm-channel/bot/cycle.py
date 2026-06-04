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

"""End-to-end cycle: pick → bench → score → build → queue."""
from __future__ import annotations

from sqlalchemy import select

from bench.registry import sync_models, sync_task_suites
from bench.runner import run_bench
from bench.scorers.pipeline import score_experiment
from bot.editorial import pick_next_rubric, seed_calendar
from content.generator import build_post
from core.db import session_scope
from core.models import Model, PostStatus


async def run_cycle(
    *,
    dry_run: bool = True,
    publish: bool = False,
    model_tag: str | None = None,
    suite_name: str = "general_ru",
) -> dict[str, int | str]:
    """Full pipeline orchestration."""
    if model_tag:
        tag = model_tag
    else:
        from scripts.ollama_preflight import resolve_bench_model

        tag = await resolve_bench_model()
    summary: dict[str, int | str] = {"model": tag, "suite": suite_name}

    async with session_scope() as session:
        await sync_models(session)
        await sync_task_suites(session)
        await seed_calendar(session)
        rubric = await pick_next_rubric(session)
        summary["rubric"] = rubric.value

        model = (
            await session.execute(select(Model).where(Model.ollama_tag == tag))
        ).scalar_one_or_none()
        if model is None:
            raise ValueError(f"Model {tag} not in registry")

        if dry_run and publish:
            summary["note"] = "dry_run ignores publish"

        exp = await run_bench(
            session,
            model_tag=tag,
            suite_name=suite_name,
            experiment_title=f"cycle {tag}",
        )
        summary["experiment_id"] = exp.id

        scored = await score_experiment(session, exp.id)
        summary["scores"] = scored

        post = await build_post(
            session,
            experiment_id=exp.id,
            post_kind=rubric,
        )
        summary["post_id"] = post.id

        if publish and not dry_run:
            from bot.review import send_for_review

            post.status = PostStatus.approved
            await session.flush()
            await send_for_review(session, post)
            summary["queued"] = "review"
        else:
            summary["queued"] = "draft"

    return summary
