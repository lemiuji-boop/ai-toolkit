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

"""Database CRUD smoke tests."""
from __future__ import annotations

import pytest
from sqlalchemy import select

from bench.registry import sync_models, sync_task_suites
from core.db import init_db, session_scope
from core.models import Model, TaskSuite


@pytest.mark.asyncio
async def test_crud_smoke() -> None:
    await init_db()
    async with session_scope() as session:
        n_models = await sync_models(session)
        n_tasks = await sync_task_suites(session)
        assert n_models > 0
        assert n_tasks > 0
        models = (await session.execute(select(Model))).scalars().all()
        suites = (await session.execute(select(TaskSuite))).scalars().all()
        assert len(models) >= 1
        assert len(suites) >= 1
