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

"""system_messages и user_preferences."""

from alembic import op
import sqlalchemy as sa

revision = "20260529_0003"
down_revision = "20260529_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("severity", sa.Enum("info", "warning", "error", name="messageseverity"), nullable=False),
        sa.Column("target_roles", sa.String(128), nullable=False),
        sa.Column("source", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("theme_id", sa.String(64), nullable=False, server_default="ocean"),
        sa.Column("dark_mode", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("catalog_root_hint", sa.String(512), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("user_preferences")
    op.drop_table("system_messages")
    op.execute("DROP TYPE IF EXISTS messageseverity")
