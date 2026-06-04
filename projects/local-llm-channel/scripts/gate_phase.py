#!/usr/bin/env python3
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

"""Phase gate checks — exit 0 on PASS."""
from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

import typer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

app = typer.Typer()


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise typer.Exit(1)


async def _latest_experiment_id() -> int:
    from sqlalchemy import select

    from core.db import session_scope
    from core.models import Experiment

    async with session_scope() as session:
        e = (await session.execute(select(Experiment).order_by(Experiment.id.desc()))).scalar()
        if not e:
            _fail("no experiments in DB")
        return e.id


async def _latest_post_id() -> int:
    from sqlalchemy import select

    from core.db import session_scope
    from core.models import Post

    async with session_scope() as session:
        p = (await session.execute(select(Post).order_by(Post.id.desc()))).scalar()
        if not p:
            _fail("no posts in DB")
        return p.id


def gate_phase_0() -> None:
    code, out = _run([sys.executable, "cli.py", "--help"])
    if code != 0:
        _fail(f"cli --help: {out}")
    code, out = _run(["ruff", "check", "."])
    if code != 0:
        _fail(f"ruff: {out}")
    print("PASS phase 0")


def gate_phase_1() -> None:
    _run([sys.executable, "cli.py", "init-db"])
    _run(["alembic", "upgrade", "head"])
    code, out = _run([sys.executable, "-m", "pytest", "tests/test_db_smoke.py", "-q"])
    if code != 0:
        _fail(f"pytest db smoke: {out}")
    print("PASS phase 1")


def gate_phase_2() -> None:
    _run([sys.executable, "cli.py", "init-db"])
    _run([sys.executable, "cli.py", "models", "sync"])
    _run([sys.executable, "cli.py", "tasks", "list"])
    code, out = _run([sys.executable, "cli.py", "models", "list"])
    if code != 0 or "ollama_tag" not in out.lower() and "llama" not in out.lower():
        _fail(f"models list: {out}")
    code, out = _run([sys.executable, "cli.py", "tasks", "list"])
    if code != 0 or "general_ru" not in out:
        _fail(f"tasks list: {out}")
    print("PASS phase 2")


def gate_phase_3() -> None:
    from scripts.ollama_preflight import check_ollama, resolve_bench_model

    if not asyncio.run(check_ollama()):
        _fail("Ollama not reachable")
    bench_model = asyncio.run(resolve_bench_model())

    _run([sys.executable, "cli.py", "models", "sync"])
    code, out = _run(
        [
            sys.executable,
            "cli.py",
            "run-bench",
            "--model",
            bench_model,
            "--suite",
            "general_ru",
        ]
    )
    if code != 0:
        _fail(f"run-bench: {out}")
    if not list((ROOT / "bench" / "results").glob("*.jsonl")):
        _fail("no bench/results/*.jsonl")

    async def _db() -> None:
        from sqlalchemy import select

        from core.db import session_scope
        from core.models import Metric, Run

        async with session_scope() as session:
            if not (await session.execute(select(Run))).scalars().all():
                _fail("no Run in DB")
            if not (await session.execute(select(Metric))).scalars().all():
                _fail("no Metric in DB")

    asyncio.run(_db())
    print("PASS phase 3")


def gate_phase_4() -> None:
    from sqlalchemy.orm import selectinload

    from bench.scorers.pipeline import score_experiment
    from core.db import session_scope
    from core.models import Experiment, Run

    async def _go() -> None:
        exp_id = await _latest_experiment_id()
        async with session_scope() as session:
            await score_experiment(session, exp_id)
            exp = await session.get(
                Experiment,
                exp_id,
                options=[selectinload(Experiment.runs).selectinload(Run.scores)],
            )
            assert exp
            for run in exp.runs:
                if run.output_text and not run.scores:
                    _fail(f"run {run.id} missing score")

    asyncio.run(_go())
    exp_id = asyncio.run(_latest_experiment_id())
    code, out = _run(
        [sys.executable, "cli.py", "scores-show", "--experiment", str(exp_id)]
    )
    if code != 0:
        _fail(f"scores-show: {out}")
    print("PASS phase 4")


def gate_phase_5() -> None:
    from bench.scorers.pipeline import score_experiment
    from content.render import TG_MESSAGE_MAX
    from core.db import session_scope
    from core.models import Post

    exp_id = asyncio.run(_latest_experiment_id())

    async def _score() -> None:
        async with session_scope() as session:
            await score_experiment(session, exp_id)

    asyncio.run(_score())
    code, out = _run(
        [
            sys.executable,
            "cli.py",
            "build-post",
            "--type",
            "head_to_head",
            "--experiment",
            str(exp_id),
        ]
    )
    if code != 0:
        _fail(f"build-post: {out}")

    async def _post() -> None:
        async with session_scope() as session:
            pid = await _latest_post_id()
            post = await session.get(Post, pid)
            assert post
            if len(post.body_md) > TG_MESSAGE_MAX:
                _fail(f"body too long: {len(post.body_md)}")

    asyncio.run(_post())
    print("PASS phase 5")


def gate_phase_6() -> None:
    from core.config import get_settings

    settings = get_settings()
    if not settings.tg_bot_token or not settings.tg_test_channel_id:
        print("SKIP phase 6: TG_BOT_TOKEN or TG_TEST_CHANNEL_ID not set (passed_with_skip)")
        print("PASS phase 6 (skip)")
        return
    exp_id = asyncio.run(_latest_experiment_id())

    async def _prepare() -> int:
        from bench.scorers.pipeline import score_experiment
        from content.generator import build_post
        from core.db import session_scope
        from core.models import ExperimentKind, PostStatus

        async with session_scope() as session:
            await score_experiment(session, exp_id)
            post = await build_post(
                session,
                experiment_id=exp_id,
                post_kind=ExperimentKind.head_to_head,
            )
            post.status = PostStatus.approved
            await session.flush()
            return post.id

    post_id = asyncio.run(_prepare())
    code, out = _run([sys.executable, "cli.py", "publish", "--post", str(post_id)])
    if code != 0:
        _fail(f"publish: {out}")
    print("PASS phase 6")


def gate_phase_7() -> None:
    code, out = _run([sys.executable, "cli.py", "cycle", "--dry-run"])
    if code != 0:
        _fail(f"cycle dry-run: {out}")
    print("PASS phase 7")


def gate_phase_8() -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        _fail("README.md missing")
    text = readme.read_text(encoding="utf-8")
    for section in ("Ollama", "миграц", ".env", "cycle"):
        if section.lower() not in text.lower():
            _fail(f"README missing section hint: {section}")
    code, out = _run([sys.executable, "-m", "pytest", "-q"])
    if code != 0:
        _fail(f"pytest: {out}")
    code, out = _run(["ruff", "check", "."])
    if code != 0:
        _fail(f"ruff: {out}")
    code, out = _run(["mypy", "core", "bench", "content", "bot"])
    if code != 0:
        _fail(f"mypy: {out}")
    print("PASS phase 8")


GATES = {
    0: gate_phase_0,
    1: gate_phase_1,
    2: gate_phase_2,
    3: gate_phase_3,
    4: gate_phase_4,
    5: gate_phase_5,
    6: gate_phase_6,
    7: gate_phase_7,
    8: gate_phase_8,
}


@app.command()
def main(phase: int = typer.Option(..., "--phase")) -> None:
    """Run gate for phase N."""
    if phase not in GATES:
        _fail(f"unknown phase {phase}")
    GATES[phase]()
    raise typer.Exit(0)


if __name__ == "__main__":
    app()
