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

"""Точка входа Celery worker для portable EXE."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _frozen() -> bool:
    return getattr(sys, "frozen", False)


def _exe_dir() -> Path:
    if _frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _deploy_root() -> Path:
    base = _exe_dir()
    if (base.parent / ".env").is_file() or (base.parent / ".env.example").is_file():
        return base.parent
    return base


def _setup_paths() -> None:
    if _frozen():
        base = _exe_dir()
        root = _deploy_root()
        os.chdir(root)
        internal = base / "_internal"
        for candidate in (base, internal):
            if candidate.exists() and str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
    else:
        backend = Path(__file__).resolve().parent
        project = backend.parent
        os.chdir(project)
        if str(backend) not in sys.path:
            sys.path.insert(0, str(backend))


def main() -> None:
    _setup_paths()
    from app.tasks.celery_app import celery_app

    celery_app.worker_main(argv=["worker", "--beat", "--loglevel=INFO", "-Q", "celery"])


if __name__ == "__main__":
    main()
