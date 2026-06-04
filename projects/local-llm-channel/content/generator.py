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

"""Build Post drafts from experiment results."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from content.charts import bar_chart
from content.render import enforce_telegram_limits, render_template
from core.models import Experiment, ExperimentKind, Post, PostStatus, Run

MEDIA_DIR = Path("data/media")


async def build_post(
    session: AsyncSession,
    *,
    experiment_id: int,
    post_kind: ExperimentKind,
    template_name: str | None = None,
) -> Post:
    """Generate draft post with charts for an experiment."""
    exp = await session.get(Experiment, experiment_id)
    if exp is None:
        raise ValueError(f"Experiment {experiment_id} not found")

    result = await session.execute(
        select(Run)
        .where(Run.experiment_id == experiment_id)
        .options(
            selectinload(Run.model),
            selectinload(Run.metrics),
            selectinload(Run.scores),
        )
    )
    runs = list(result.scalars().all())

    labels: list[str] = []
    tok_values: list[float] = []
    vram_values: list[float] = []
    rows: list[dict[str, object]] = []

    seen_models: set[str] = set()
    for run in runs:
        tag = run.model.ollama_tag
        if tag in seen_models:
            continue
        seen_models.add(tag)
        if run.metrics:
            m = run.metrics[0]
            labels.append(run.model.name)
            tok_values.append(m.tok_per_sec)
            vram_values.append(float(m.peak_vram_mb))
            score_val = run.scores[0].value if run.scores else 0.0
            rows.append(
                {
                    "model": run.model.name,
                    "tok_s": round(m.tok_per_sec, 1),
                    "vram_mb": m.peak_vram_mb,
                    "quality": round(score_val, 2),
                }
            )

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    chart_tok = MEDIA_DIR / f"exp_{experiment_id}_tok.png"
    chart_vram = MEDIA_DIR / f"exp_{experiment_id}_vram.png"
    if labels:
        bar_chart(labels, tok_values, "Скорость (tok/s)", "tok/s", chart_tok)
        bar_chart(labels, vram_values, "Peak VRAM (MB)", "MB", chart_vram)

    tpl = template_name or _kind_to_template(post_kind)
    body = render_template(
        tpl,
        title=exp.title,
        rows=rows,
        hardware="RTX 3060 Laptop 6GB",
        methodology="3 повтора, медиана tok/s, max peak VRAM",
    )
    body = enforce_telegram_limits(body)

    post = Post(
        experiment_id=exp.id,
        kind=post_kind,
        title=exp.title,
        body_md=body,
        media_paths=[str(chart_tok), str(chart_vram)] if labels else [],
        status=PostStatus.draft,
    )
    session.add(post)
    await session.flush()
    return post


def _kind_to_template(kind: ExperimentKind) -> str:
    mapping = {
        ExperimentKind.head_to_head: "head_to_head.md.j2",
        ExperimentKind.model_review: "model_review.md.j2",
        ExperimentKind.fits_6gb: "fits_6gb.md.j2",
        ExperimentKind.benchmark_roundup: "benchmark_roundup.md.j2",
        ExperimentKind.howto: "howto.md.j2",
        ExperimentKind.news: "news.md.j2",
    }
    return mapping.get(kind, "model_review.md.j2")
