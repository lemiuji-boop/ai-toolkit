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

"""Benchmark runner: Model × Task suite."""
from __future__ import annotations

import asyncio
import json
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bench.ollama_client import OllamaClient
from bench.scorers.speed import aggregate_speed_metrics
from bench.vram import PeakVramSampler
from core.config import get_settings
from core.models import Experiment, ExperimentKind, Metric, Model, Run, RunStatus, Task, TaskSuite

RESULTS_DIR = Path(__file__).parent / "results"


async def run_bench(
    session: AsyncSession,
    *,
    model_tag: str,
    suite_name: str,
    num_ctx: int = 4096,
    experiment_title: str | None = None,
) -> Experiment:
    """Run full suite for one model; persist runs and metrics."""
    settings = get_settings()
    client = OllamaClient()
    if not await client.health():
        raise RuntimeError(f"Ollama unavailable at {settings.ollama_base_url}")

    model = (
        await session.execute(select(Model).where(Model.ollama_tag == model_tag))
    ).scalar_one_or_none()
    if model is None:
        raise ValueError(f"Model not in registry: {model_tag}")

    suite = (
        await session.execute(select(TaskSuite).where(TaskSuite.name == suite_name))
    ).scalar_one_or_none()
    if suite is None:
        raise ValueError(f"Task suite not found: {suite_name}")

    exp = Experiment(
        title=experiment_title or f"{model_tag} / {suite_name}",
        kind=ExperimentKind.model_review,
        config={
            "model": model_tag,
            "suite": suite_name,
            "num_ctx": num_ctx,
            "n_repeats": settings.n_repeats,
            "seed": settings.default_seed,
        },
    )
    session.add(exp)
    await session.flush()

    tasks = (
        await session.execute(select(Task).where(Task.suite_id == suite.id))
    ).scalars().all()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    jsonl_path = RESULTS_DIR / f"exp_{exp.id}_{model_tag.replace(':', '_')}.jsonl"

    await client.unload_model(model_tag)
    await asyncio.sleep(3)

    with jsonl_path.open("w", encoding="utf-8") as jf:
        for task in tasks:
            await _run_task_repeats(
                session,
                client,
                jf,
                exp,
                model,
                task,
                num_ctx=num_ctx,
            )

    return exp


async def _run_task_repeats(
    session: AsyncSession,
    client: OllamaClient,
    jf: Any,
    experiment: Experiment,
    model: Model,
    task: Task,
    *,
    num_ctx: int,
) -> None:
    settings = get_settings()
    # Прогрев — не учитывается в метриках БД
    await client.generate(
        model.ollama_tag,
        task.prompt,
        system=task.system_prompt,
        temperature=0.0,
        seed=settings.default_seed,
        num_ctx=num_ctx,
        num_predict=task.max_tokens,
    )

    tok_rates: list[float] = []
    peaks: list[int] = []
    last_output = ""
    last_metrics = None

    for _ in range(settings.n_repeats):
        sampler = PeakVramSampler()
        sampler.start()
        started = datetime.now(UTC)
        try:
            resp = await client.generate(
                model.ollama_tag,
                task.prompt,
                system=task.system_prompt,
                temperature=0.0,
                seed=settings.default_seed,
                num_ctx=num_ctx,
                num_predict=task.max_tokens,
            )
            status = RunStatus.ok
            err = None
            last_output = resp.text
            last_metrics = resp.metrics
            tok_rates.append(resp.metrics.tok_per_sec)
        except Exception as exc:
            status = RunStatus.error
            err = str(exc)
            resp = None
        finished = datetime.now(UTC)
        vram = await asyncio.to_thread(sampler.stop)
        peaks.append(vram.peak_mb)

        run = Run(
            experiment_id=experiment.id,
            model_id=model.id,
            task_id=task.id,
            started_at=started,
            finished_at=finished,
            seed=settings.default_seed,
            temperature=0.0,
            num_ctx=num_ctx,
            num_predict=task.max_tokens,
            output_text=last_output if resp else None,
            output_path=str(jf.name),
            status=status,
            error=err,
        )
        session.add(run)
        await session.flush()

        if resp and last_metrics:
            med_tok = statistics.median(tok_rates) if tok_rates else 0.0
            peak_vram = max(peaks) if peaks else vram.peak_mb
            ram_mb = int(psutil.virtual_memory().used / (1024 * 1024))
            metric = Metric(
                run_id=run.id,
                tok_per_sec=float(med_tok),
                ttft_ms=last_metrics.ttft_ms,
                prompt_tokens=last_metrics.prompt_tokens,
                eval_tokens=last_metrics.eval_tokens,
                peak_vram_mb=peak_vram,
                peak_ram_mb=ram_mb,
                total_ms=last_metrics.total_ms,
            )
            session.add(metric)
            record = {
                "run_id": run.id,
                "task": task.key,
                "output": last_output[:500],
                "tok_per_sec": med_tok,
                "peak_vram_mb": peak_vram,
            }
            jf.write(json.dumps(record, ensure_ascii=False) + "\n")

    await session.flush()
    if last_metrics:
        aggregate_speed_metrics(tok_rates, peaks)
