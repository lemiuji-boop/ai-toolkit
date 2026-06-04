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

"""SQLAlchemy ORM models."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base."""


class Fits6Gb(str, enum.Enum):
    yes = "yes"
    tight = "tight"
    offload = "offload"
    no = "no"


class Modality(str, enum.Enum):
    text = "text"
    vision = "vision"
    code = "code"


class TaskCategory(str, enum.Enum):
    general_ru = "general_ru"
    coding = "coding"
    reasoning = "reasoning"
    summarization_ru = "summarization_ru"
    rag = "rag"
    function_calling = "function_calling"
    long_context = "long_context"
    creative_ru = "creative_ru"


class TaskLanguage(str, enum.Enum):
    ru = "ru"
    en = "en"
    mixed = "mixed"


class ScorerType(str, enum.Enum):
    exact = "exact"
    regex = "regex"
    json_scorer = "json"
    code = "code"
    judge = "judge"


class ExperimentKind(str, enum.Enum):
    model_review = "model_review"
    head_to_head = "head_to_head"
    fits_6gb = "fits_6gb"
    benchmark_roundup = "benchmark_roundup"
    howto = "howto"
    news = "news"


class RunStatus(str, enum.Enum):
    ok = "ok"
    error = "error"
    oom = "oom"


class PostStatus(str, enum.Enum):
    draft = "draft"
    review = "review"
    approved = "approved"
    scheduled = "scheduled"
    published = "published"
    rejected = "rejected"


class Model(Base):
    __tablename__ = "models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    ollama_tag: Mapped[str] = mapped_column(String(128), unique=True)
    params_b: Mapped[float] = mapped_column(Float)
    quant: Mapped[str] = mapped_column(String(32), default="Q4_K_M")
    family: Mapped[str] = mapped_column(String(64))
    est_vram_gb: Mapped[float] = mapped_column(Float)
    fits_6gb: Mapped[Fits6Gb] = mapped_column(Enum(Fits6Gb))
    context_max: Mapped[int] = mapped_column(Integer, default=8192)
    modality: Mapped[Modality] = mapped_column(Enum(Modality), default=Modality.text)
    license: Mapped[str] = mapped_column(String(64), default="")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    runs: Mapped[list[Run]] = relationship(back_populates="model")


class TaskSuite(Base):
    __tablename__ = "task_suites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    category: Mapped[TaskCategory] = mapped_column(Enum(TaskCategory))
    language: Mapped[TaskLanguage] = mapped_column(Enum(TaskLanguage))
    description: Mapped[str] = mapped_column(Text, default="")

    tasks: Mapped[list[Task]] = relationship(back_populates="suite")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suite_id: Mapped[int] = mapped_column(ForeignKey("task_suites.id"))
    key: Mapped[str] = mapped_column(String(64))
    prompt: Mapped[str] = mapped_column(Text)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected: Mapped[str | None] = mapped_column(Text, nullable=True)
    scorer: Mapped[ScorerType] = mapped_column(Enum(ScorerType))
    scorer_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    max_tokens: Mapped[int] = mapped_column(Integer, default=256)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    suite: Mapped[TaskSuite] = relationship(back_populates="tasks")
    runs: Mapped[list[Run]] = relationship(back_populates="task")


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    kind: Mapped[ExperimentKind] = mapped_column(Enum(ExperimentKind))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    runs: Mapped[list[Run]] = relationship(back_populates="experiment")
    posts: Mapped[list[Post]] = relationship(back_populates="experiment")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id"))
    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    seed: Mapped[int] = mapped_column(Integer)
    temperature: Mapped[float] = mapped_column(Float)
    num_ctx: Mapped[int] = mapped_column(Integer)
    num_predict: Mapped[int] = mapped_column(Integer)
    output_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[RunStatus] = mapped_column(Enum(RunStatus))
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    experiment: Mapped[Experiment] = relationship(back_populates="runs")
    model: Mapped[Model] = relationship(back_populates="runs")
    task: Mapped[Task] = relationship(back_populates="runs")
    metrics: Mapped[list[Metric]] = relationship(back_populates="run")
    scores: Mapped[list[Score]] = relationship(back_populates="run")


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    tok_per_sec: Mapped[float] = mapped_column(Float)
    ttft_ms: Mapped[float] = mapped_column(Float)
    prompt_tokens: Mapped[int] = mapped_column(Integer)
    eval_tokens: Mapped[int] = mapped_column(Integer)
    peak_vram_mb: Mapped[int] = mapped_column(Integer)
    peak_ram_mb: Mapped[int] = mapped_column(Integer)
    total_ms: Mapped[float] = mapped_column(Float)

    run: Mapped[Run] = relationship(back_populates="metrics")


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"))
    scorer: Mapped[str] = mapped_column(String(64))
    value: Mapped[float] = mapped_column(Float)
    raw: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    run: Mapped[Run] = relationship(back_populates="scores")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    experiment_id: Mapped[int | None] = mapped_column(
        ForeignKey("experiments.id"), nullable=True
    )
    kind: Mapped[ExperimentKind] = mapped_column(Enum(ExperimentKind))
    title: Mapped[str] = mapped_column(String(256))
    body_md: Mapped[str] = mapped_column(Text)
    media_paths: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.draft)
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    tg_message_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    experiment: Mapped[Experiment | None] = relationship(back_populates="posts")


class CalendarSlot(Base):
    __tablename__ = "calendar_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    weekday: Mapped[int] = mapped_column(Integer)
    time_local: Mapped[str] = mapped_column(String(8))
    rubric: Mapped[ExperimentKind] = mapped_column(Enum(ExperimentKind))
    active: Mapped[bool] = mapped_column(default=True)
