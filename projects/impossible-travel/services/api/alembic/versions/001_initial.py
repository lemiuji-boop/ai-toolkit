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

"""initial

Revision ID: 001
Revises:
Create Date: 2026-06-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "brand_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), unique=True),
        sa.Column("brand_voice", sa.String(512), nullable=False),
        sa.Column("visual_identity", sa.String(512), nullable=False),
        sa.Column("content_pillars", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "episodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("topic", sa.String(512), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("status", sa.String(32), server_default="draft"),
        sa.Column("language", sa.String(8), server_default="ru"),
        sa.Column("duration_target", sa.Integer(), server_default="60"),
        sa.Column("platforms", postgresql.JSONB(), nullable=True),
        sa.Column("style", sa.String(256)),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("main_character_id", sa.String(64), server_default="main_girl"),
        sa.Column("idea", postgresql.JSONB(), nullable=True),
        sa.Column("worldbuilding", postgresql.JSONB(), nullable=True),
        sa.Column("science_check", postgresql.JSONB(), nullable=True),
        sa.Column("architect", postgresql.JSONB(), nullable=True),
        sa.Column("script", sa.Text(), nullable=True),
        sa.Column("shotlist", postgresql.JSONB(), nullable=True),
        sa.Column("visual_style", postgresql.JSONB(), nullable=True),
        sa.Column("platform_packages", postgresql.JSONB(), nullable=True),
        sa.Column("compliance_report", postgresql.JSONB(), nullable=True),
        sa.Column("quality_report", postgresql.JSONB(), nullable=True),
        sa.Column("episode_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "characters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("external_id", sa.String(64), index=True),
        sa.Column("name", sa.String(128)),
        sa.Column("role", sa.String(128)),
        sa.Column("bible", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id")),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id"), nullable=True),
        sa.Column("name", sa.String(255)),
        sa.Column("location_type", sa.String(128)),
        sa.Column("data", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_foreign_key("fk_episodes_location", "episodes", "locations", ["location_id"], ["id"])
    op.create_table(
        "scenes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("order_index", sa.Integer(), default=0),
        sa.Column("title", sa.String(255)),
        sa.Column("time_range", sa.String(32), nullable=True),
        sa.Column("data", postgresql.JSONB()),
    )
    op.create_table(
        "shots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("scene_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("scenes.id"), nullable=True),
        sa.Column("shot_external_id", sa.String(32)),
        sa.Column("duration", sa.Integer(), default=5),
        sa.Column("camera", sa.String(256), nullable=True),
        sa.Column("subject", sa.String(512), nullable=True),
        sa.Column("location_text", sa.String(512), nullable=True),
        sa.Column("visual_prompt", sa.Text(), nullable=True),
        sa.Column("negative_prompt", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), default=0),
    )
    op.create_table(
        "prompts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("shot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shots.id"), nullable=True),
        sa.Column("prompt_type", sa.String(64)),
        sa.Column("content", sa.Text()),
        sa.Column("negative_content", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("shot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shots.id"), nullable=True),
        sa.Column("asset_type", sa.String(32)),
        sa.Column("storage_key", sa.String(1024)),
        sa.Column("url", sa.String(2048)),
        sa.Column("meta", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "generation_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("step", sa.String(128)),
        sa.Column("status", sa.String(32), server_default="pending"),
        sa.Column("progress", sa.Float(), default=0.0),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "quality_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("gates", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "compliance_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("decision", sa.String(32)),
        sa.Column("disclosure_text", postgresql.JSONB()),
        sa.Column("details", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "publications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id", ondelete="CASCADE")),
        sa.Column("platform", sa.String(64)),
        sa.Column("status", sa.String(32), server_default="draft"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "monetization_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id"), nullable=True),
        sa.Column("label", sa.String(255)),
        sa.Column("url", sa.String(1024)),
        sa.Column("disclosed", sa.Boolean(), default=True),
    )
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("episodes.id"), nullable=True),
        sa.Column("event_type", sa.String(64)),
        sa.Column("payload", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in [
        "analytics_events",
        "monetization_links",
        "publications",
        "compliance_reports",
        "quality_reports",
        "generation_tasks",
        "assets",
        "prompts",
        "shots",
        "scenes",
        "locations",
        "characters",
        "episodes",
        "brand_profiles",
        "projects",
    ]:
        op.drop_table(table)
