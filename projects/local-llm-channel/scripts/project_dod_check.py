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

"""Full project DoD check (TZ section 14)."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT).returncode


def main() -> int:
    checks = [
        (["uv", "run", "pytest", "-q"], "pytest"),
        (["uv", "run", "ruff", "check", "."], "ruff"),
        (["uv", "run", "mypy", "core", "bench", "content", "bot"], "mypy"),
        (["uv", "run", "python", "scripts/gate_phase.py", "--phase", "8"], "gate-8"),
        (["uv", "run", "python", "cli.py", "cycle", "--dry-run"], "cycle-dry-run"),
    ]
    failed = []
    for cmd, name in checks:
        if run(cmd) != 0:
            failed.append(name)
    if failed:
        print("PROJECT_DOD: FAIL")
        print("GAPS:", ", ".join(failed))
        return 1
    print("PROJECT_DOD: PASS")
    print("SUMMARY: pytest, ruff, mypy, gate 8, cycle --dry-run OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
