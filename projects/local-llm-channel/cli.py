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

"""Typer CLI entrypoint for llm-channel."""
from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy import select

from bench.registry import sync_models, sync_task_suites
from bench.runner import run_bench
from bench.scorers.pipeline import score_experiment
from bot.cycle import run_cycle
from bot.publisher import publish_post
from bot.scheduler import start_scheduler
from content.generator import build_post
from core.db import init_db, session_scope
from core.models import Experiment, ExperimentKind, Model, Post, TaskSuite

app = typer.Typer(help="LLM channel — bench, content, publish")
models_app = typer.Typer(help="Model registry")
tasks_app = typer.Typer(help="Task suites")
app.add_typer(models_app, name="models")
app.add_typer(tasks_app, name="tasks")
console = Console()


def _run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


@models_app.command("list")
def models_list() -> None:
    """List models from database."""

    async def _inner() -> None:
        async with session_scope() as session:
            await sync_models(session)
            result = await session.execute(select(Model))
            rows = result.scalars().all()
        table = Table(title="Models")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Tag")
        table.add_column("Fits 6GB")
        for m in rows:
            table.add_row(str(m.id), m.name, m.ollama_tag, m.fits_6gb.value)
        console.print(table)
        if not rows:
            raise typer.Exit(1)

    _run(_inner())


@models_app.command("sync")
def models_sync() -> None:
    """Sync models.yaml into database."""

    async def _inner() -> None:
        async with session_scope() as session:
            n = await sync_models(session)
        console.print(f"Synced {n} models")

    _run(_inner())


@tasks_app.command("list")
def tasks_list() -> None:
    """List task suites from database."""

    async def _inner() -> None:
        async with session_scope() as session:
            await sync_task_suites(session)
            result = await session.execute(select(TaskSuite))
            rows = result.scalars().all()
        table = Table(title="Task suites")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Category")
        for s in rows:
            table.add_row(str(s.id), s.name, s.category.value)
        console.print(table)
        if not rows:
            raise typer.Exit(1)

    _run(_inner())


@app.command("init-db")
def init_db_cmd() -> None:
    """Create database tables."""

    async def _inner() -> None:
        await init_db()
        console.print("Database initialized")

    _run(_inner())


@app.command("run-bench")
def run_bench_cmd(
    model: str = typer.Option(..., "--model"),
    suite: str = typer.Option(..., "--suite"),
    ctx: int = typer.Option(4096, "--ctx"),
) -> None:
    """Run benchmark for model and suite."""

    async def _inner() -> None:
        async with session_scope() as session:
            await sync_models(session)
            await sync_task_suites(session)
            exp = await run_bench(session, model_tag=model, suite_name=suite, num_ctx=ctx)
        console.print(f"Experiment id={exp.id}")

    _run(_inner())


@app.command("run-experiment")
def run_experiment_cmd(
    kind: str = typer.Option("head_to_head", "--kind"),
    models: str = typer.Option(..., "--models", help="Comma-separated ollama tags"),
    suites: str = typer.Option("general_ru", "--suites"),
) -> None:
    """Run experiment across multiple models."""

    async def _inner() -> None:
        tags = [m.strip() for m in models.split(",")]
        suite_list = [s.strip() for s in suites.split(",")]
        last_id = 0
        async with session_scope() as session:
            await sync_models(session)
            await sync_task_suites(session)
            for tag in tags:
                for suite in suite_list:
                    exp = await run_bench(
                        session,
                        model_tag=tag,
                        suite_name=suite,
                        experiment_title=f"{kind} {tag}",
                    )
                    last_id = exp.id
        console.print(f"Last experiment id={last_id}")

    _run(_inner())


@app.command("scores")
def scores_group() -> None:
    """Scores commands — use scores-show subcommand via typer."""
    console.print("Use: python cli.py scores-show --experiment ID")


@app.command("scores-show")
def scores_show(experiment: int = typer.Option(..., "--experiment")) -> None:
    """Show score summary for experiment."""

    async def _inner() -> None:
        async with session_scope() as session:
            await score_experiment(session, experiment)
            from sqlalchemy.orm import selectinload

            from core.models import Run

            exp = await session.get(
                Experiment,
                experiment,
                options=[
                    selectinload(Experiment.runs).selectinload(Run.scores),
                    selectinload(Experiment.runs).selectinload(Run.model),
                ],
            )
            if not exp:
                raise typer.Exit(1)
            table = Table(title=f"Scores exp={experiment}")
            table.add_column("Run")
            table.add_column("Model")
            table.add_column("Score")
            for run in exp.runs:
                sc = run.scores[0].value if run.scores else 0.0
                table.add_row(str(run.id), run.model.ollama_tag, f"{sc:.2f}")
            console.print(table)

    _run(_inner())


@app.command("build-post")
def build_post_cmd(
    type: str = typer.Option(..., "--type"),
    experiment: int = typer.Option(..., "--experiment"),
) -> None:
    """Build draft post from experiment."""

    async def _inner() -> None:
        kind = ExperimentKind(type)
        async with session_scope() as session:
            post = await build_post(session, experiment_id=experiment, post_kind=kind)
        console.print(f"Post id={post.id} len={len(post.body_md)}")

    _run(_inner())


@app.command("publish")
def publish_cmd(post_id: int = typer.Option(..., "--post")) -> None:
    """Publish approved post."""

    async def _inner() -> None:
        from core.models import PostStatus

        async with session_scope() as session:
            post = await session.get(Post, post_id)
            if not post:
                raise typer.Exit(1)
            post.status = PostStatus.approved
            msg_id = await publish_post(session, post)
        console.print(f"Published message_id={msg_id}")

    _run(_inner())


@app.command("cycle")
def cycle_cmd(
    dry_run: bool = typer.Option(True, "--dry-run"),
    publish: bool = typer.Option(False, "--publish"),
    model: str | None = typer.Option(None, "--model"),
) -> None:
    """Full pipeline cycle."""

    async def _inner() -> None:
        summary = await run_cycle(dry_run=dry_run, publish=publish, model_tag=model)
        console.print(summary)

    _run(_inner())


@app.command("bot")
def bot_run() -> None:
    """Run bot scheduler (blocking)."""
    start_scheduler()
    console.print("Scheduler started. Press Ctrl+C to exit.")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    app()
