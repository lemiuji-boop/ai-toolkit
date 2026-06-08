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

"""extension per CURSOR_ДОРАБОТКА"""

from alembic import op
import sqlalchemy as sa

revision = "20260529_0002"
down_revision = "20260528_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Роли: пересоздаём enum userrole
    op.execute("ALTER TYPE userrole RENAME TO userrole_old")
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'moderator', 'user')")
    op.execute(
        "ALTER TABLE users ALTER COLUMN role TYPE userrole USING "
        "CASE role::text "
        "WHEN 'engineer' THEN 'moderator'::userrole "
        "WHEN 'guest' THEN 'user'::userrole "
        "ELSE role::text::userrole END"
    )
    op.execute("DROP TYPE userrole_old")

    op.add_column("users", sa.Column("full_name", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.String(64), nullable=True))

    op.add_column("documents", sa.Column("product_number", sa.String(128), nullable=True))
    op.add_column("documents", sa.Column("catalog_path", sa.String(512), nullable=True))
    op.add_column("documents", sa.Column("source_file_hash", sa.String(128), nullable=True))
    op.add_column("documents", sa.Column("ocr_processed", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("documents", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("ALTER TYPE documentstatus ADD VALUE IF NOT EXISTS 'needs_review'")

    op.create_index("idx_documents_product", "documents", ["product_number"])
    op.create_index("idx_documents_catalog_path", "documents", ["catalog_path"])
    op.create_index("idx_documents_source_hash", "documents", ["source_file_hash"])

    # change_orders: убрать document_id, добавить поля ИИ
    op.drop_constraint("change_orders_document_id_fkey", "change_orders", type_="foreignkey")
    op.drop_column("change_orders", "document_id")
    op.drop_column("change_orders", "applied_at")
    op.add_column("change_orders", sa.Column("issue_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("change_orders", sa.Column("file_path", sa.String(512), nullable=True))
    op.add_column("change_orders", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("change_orders", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("change_orders", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.create_unique_constraint("uq_change_orders_order_number", "change_orders", ["order_number"])
    op.create_index("idx_change_orders_order_number", "change_orders", ["order_number"])

    op.create_table(
        "change_order_directives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("change_order_id", sa.Integer(), sa.ForeignKey("change_orders.id"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("affected_doc_number", sa.String(128), nullable=True),
        sa.Column("backlog_action", sa.Enum("use", "rework", "fix", "scrap", name="backlogaction"), nullable=True),
        sa.Column(
            "implementation_kind",
            sa.Enum("from_product", "from_date", "immediate", name="implementationkind"),
            nullable=True,
        ),
        sa.Column("implementation_product", sa.String(128), nullable=True),
        sa.Column("implementation_date", sa.Date(), nullable=True),
        sa.Column("directive_text", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
    )
    op.create_index("idx_directives_backlog", "change_order_directives", ["backlog_action"])
    op.create_index("idx_directives_impl_date", "change_order_directives", ["implementation_date"])
    op.create_index("idx_directives_affected_doc", "change_order_directives", ["affected_doc_number"])

    op.create_table(
        "record_revisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "target_type",
            sa.Enum("document", "change_order", "directive", "relation", name="revisiontargettype"),
            nullable=False,
        ),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.Enum("create", "update", "delete", "move", name="revisionaction"), nullable=False),
        sa.Column("changed_fields", sa.JSON(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
    )
    op.create_index("idx_revisions_target", "record_revisions", ["target_type", "target_id"])

    op.create_table(
        "ai_providers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider_type", sa.Enum("local", "external", name="aiprovidertype"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("base_url", sa.String(512), nullable=False),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("model_name", sa.String(128), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "ai_provider_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("allow_external_providers", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("active_provider_id", sa.Integer(), nullable=True),
    )

    op.create_table(
        "inbox_pending",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("file_path", sa.String(512), nullable=False, unique=True),
        sa.Column("file_hash", sa.String(128), nullable=False),
        sa.Column("status", sa.String(32), server_default="needs_review", nullable=False),
        sa.Column("reason", sa.String(255), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("inbox_pending")
    op.drop_table("ai_provider_settings")
    op.drop_table("ai_providers")
    op.drop_table("record_revisions")
    op.drop_table("change_order_directives")
    op.drop_column("change_orders", "deleted_at")
    op.drop_column("change_orders", "updated_at")
    op.drop_column("change_orders", "created_at")
    op.drop_column("change_orders", "file_path")
    op.drop_column("change_orders", "issue_date")
    op.add_column("change_orders", sa.Column("document_id", sa.Integer(), nullable=True))
    op.add_column("change_orders", sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True))

    op.drop_column("documents", "deleted_at")
    op.drop_column("documents", "ocr_processed")
    op.drop_column("documents", "source_file_hash")
    op.drop_column("documents", "catalog_path")
    op.drop_column("documents", "product_number")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "full_name")
