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

"""FastAPI admin API (optional)."""
from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import select

from core.db import session_scope
from core.models import Experiment, Post
from core.schemas import PostRead

app = FastAPI(title="LLM Channel Admin")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/experiments")
async def list_experiments() -> list[dict[str, int | str]]:
    async with session_scope() as session:
        result = await session.execute(select(Experiment).limit(50))
        return [{"id": e.id, "title": e.title, "kind": e.kind.value} for e in result.scalars()]


@app.get("/posts/{post_id}", response_model=PostRead)
async def get_post(post_id: int) -> PostRead:
    async with session_scope() as session:
        post = await session.get(Post, post_id)
        if not post:
            from fastapi import HTTPException

            raise HTTPException(404)
        return PostRead.model_validate(post)
