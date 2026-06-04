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

"""Pydantic DTOs for API and CLI."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from core.models import ExperimentKind, Fits6Gb, PostStatus, RunStatus


class ModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ollama_tag: str
    params_b: float
    quant: str
    family: str
    est_vram_gb: float
    fits_6gb: Fits6Gb
    context_max: int


class TaskSuiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    language: str
    description: str


class RunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiment_id: int
    model_id: int
    task_id: int
    status: RunStatus
    output_text: str | None


class MetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tok_per_sec: float
    ttft_ms: float
    peak_vram_mb: int


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: ExperimentKind
    title: str
    body_md: str
    status: PostStatus
    media_paths: list[str]
