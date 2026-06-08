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

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class RevisionStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    LOCKED = "locked"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    password_hash: Mapped[str] = mapped_column(String(512))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.ACTIVE)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    roles: Mapped[list["UserRole"]] = relationship(back_populates="user")


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")

    permissions: Mapped[list["RolePermission"]] = relationship(back_populates="role")
    users: Mapped[list["UserRole"]] = relationship(back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))

    user: Mapped[User] = relationship(back_populates="roles")
    role: Mapped[Role] = relationship(back_populates="users")


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    permission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE")
    )

    role: Mapped[Role] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(64))
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    calculations: Mapped[list["Calculation"]] = relationship(back_populates="project")


class Calculation(Base, TimestampMixin):
    __tablename__ = "calculations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    designation: Mapped[str] = mapped_column(String(128), default="")
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    project: Mapped[Project] = relationship(back_populates="calculations")
    revisions: Mapped[list["CalculationRevision"]] = relationship(back_populates="calculation")


class CalculationRevision(Base, TimestampMixin):
    __tablename__ = "calculation_revisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("calculations.id", ondelete="CASCADE")
    )
    revision_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[RevisionStatus] = mapped_column(
        Enum(RevisionStatus), default=RevisionStatus.DRAFT
    )
    note: Mapped[str] = mapped_column(Text, default="")
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    calculation: Mapped["Calculation"] = relationship(back_populates="revisions")


class StoredFile(Base, TimestampMixin):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("calculations.id"), nullable=True
    )
    original_name: Mapped[str] = mapped_column(String(512))
    mime_type: Mapped[str] = mapped_column(String(128))
    size_bytes: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(String(1024))
    sha256: Mapped[str] = mapped_column(String(64))
    is_quarantined: Mapped[bool] = mapped_column(Boolean, default=True)
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"))
    document_type: Mapped[str] = mapped_column(String(64), default="unknown")
    is_scan: Mapped[bool] = mapped_column(Boolean, default=False)
    has_text_layer: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(16), default="ru")
    page_count: Mapped[int] = mapped_column(Integer, default=0)
    quality_score: Mapped[float | None] = mapped_column(nullable=True)


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    page_number: Mapped[int] = mapped_column(Integer)
    image_storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    ocr_storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)


class SpecRow(Base, TimestampMixin):
    __tablename__ = "spec_rows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    position: Mapped[str | None] = mapped_column(String(32), nullable=True)
    designation: Mapped[str | None] = mapped_column(String(128), nullable=True)
    name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    quantity: Mapped[float | None] = mapped_column(nullable=True)
    section: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float] = mapped_column(default=0.0)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AssemblyLink(Base, TimestampMixin):
    __tablename__ = "assembly_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calculations.id", ondelete="CASCADE"))
    parent_designation: Mapped[str] = mapped_column(String(128))
    child_designation: Mapped[str] = mapped_column(String(128))
    quantity: Mapped[float] = mapped_column(default=1.0)
    confidence: Mapped[float] = mapped_column(default=0.8)
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )


class ExtractedFact(Base, TimestampMixin):
    __tablename__ = "extracted_facts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    field: Mapped[str] = mapped_column(String(128))
    value: Mapped[str] = mapped_column(Text)
    original_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox: Mapped[list | None] = mapped_column(JSON, nullable=True)
    method: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(default=0.0)
    evidence_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_user_corrected: Mapped[bool] = mapped_column(Boolean, default=False)
    review_status: Mapped[str] = mapped_column(String(32), default="pending")
    created_by: Mapped[str] = mapped_column(String(32), default="system")


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("calculations.id"), nullable=True
    )
    job_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    rq_job_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


class JobEvent(Base):
    __tablename__ = "job_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class KsiNode(Base, TimestampMixin):
    __tablename__ = "ksi_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calculations.id", ondelete="CASCADE"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ksi_nodes.id"), nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=0)
    designation: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(512))
    node_type: Mapped[str] = mapped_column(String(32), default="detail")
    quantity_per_parent: Mapped[float] = mapped_column(default=1.0)
    quantity_total: Mapped[float] = mapped_column(default=1.0)
    source_document_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(default=1.0)


class Material(Base, TimestampMixin):
    __tablename__ = "materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    material_type: Mapped[str] = mapped_column(String(64))
    unit: Mapped[str] = mapped_column(String(16), default="kg")
    density: Mapped[float | None] = mapped_column(nullable=True)


class KimRule(Base, TimestampMixin):
    __tablename__ = "kim_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_type: Mapped[str] = mapped_column(String(64))
    process_type: Mapped[str] = mapped_column(String(64))
    kim_value: Mapped[float] = mapped_column()
    description: Mapped[str] = mapped_column(String(255), default="")


class AllowanceRule(Base, TimestampMixin):
    __tablename__ = "allowance_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_type: Mapped[str] = mapped_column(String(64))
    thickness_min: Mapped[float | None] = mapped_column(nullable=True)
    thickness_max: Mapped[float | None] = mapped_column(nullable=True)
    allowance_value: Mapped[float] = mapped_column()
    description: Mapped[str] = mapped_column(String(255), default="")


class CalculationItem(Base, TimestampMixin):
    __tablename__ = "calculation_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calculations.id", ondelete="CASCADE"))
    revision_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("calculation_revisions.id"), nullable=True
    )
    material_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("materials.id"), nullable=True)
    material_name: Mapped[str] = mapped_column(String(255))
    net_qty: Mapped[float] = mapped_column()
    gross_qty: Mapped[float] = mapped_column()
    unit: Mapped[str] = mapped_column(String(16))
    kim: Mapped[float | None] = mapped_column(nullable=True)
    allowance: Mapped[float | None] = mapped_column(nullable=True)
    waste: Mapped[float | None] = mapped_column(nullable=True)
    formula: Mapped[str] = mapped_column(Text)
    rule_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_facts: Mapped[list | None] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(default=1.0)
    requires_review: Mapped[bool] = mapped_column(Boolean, default=False)
    is_auxiliary: Mapped[bool] = mapped_column(Boolean, default=False)


class AiProvider(Base, TimestampMixin):
    __tablename__ = "ai_providers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    provider_type: Mapped[str] = mapped_column(String(32))
    base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)


class AiModel(Base, TimestampMixin):
    __tablename__ = "ai_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_providers.id", ondelete="CASCADE"))
    model_name: Mapped[str] = mapped_column(String(128))
    task_types: Mapped[list] = mapped_column(JSON, default=list)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class AiRequest(Base):
    __tablename__ = "ai_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ai_providers.id"), nullable=True)
    task_type: Mapped[str] = mapped_column(String(64))
    model_name: Mapped[str] = mapped_column(String(128))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ApiKeySecret(Base, TimestampMixin):
    __tablename__ = "api_key_secrets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_providers.id", ondelete="CASCADE"))
    encrypted_value: Mapped[str] = mapped_column(Text)


class ExcelTemplate(Base, TimestampMixin):
    __tablename__ = "excel_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    version: Mapped[int] = mapped_column(Integer, default=1)
    storage_key: Mapped[str] = mapped_column(String(1024))
    field_mapping: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class ExcelExport(Base, TimestampMixin):
    __tablename__ = "excel_exports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calculations.id"))
    revision_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("calculation_revisions.id"), nullable=True
    )
    template_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("excel_templates.id"), nullable=True)
    storage_key: Mapped[str] = mapped_column(String(1024))


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserCorrection(Base, TimestampMixin):
    __tablename__ = "user_corrections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("extracted_facts.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    old_value: Mapped[str] = mapped_column(Text)
    new_value: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class LearningExample(Base, TimestampMixin):
    __tablename__ = "learning_examples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    example_type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="candidate")


class AuxMaterialRule(Base, TimestampMixin):
    __tablename__ = "aux_material_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_type: Mapped[str] = mapped_column(String(64))
    material_name: Mapped[str] = mapped_column(String(255))
    rate_per_unit: Mapped[float] = mapped_column(default=0.0)
    unit: Mapped[str] = mapped_column(String(16), default="kg")
    description: Mapped[str] = mapped_column(String(255), default="")


class ProcessRule(Base, TimestampMixin):
    __tablename__ = "process_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_type: Mapped[str] = mapped_column(String(64))
    process_type: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(255), default="")


class MaterialAlias(Base, TimestampMixin):
    __tablename__ = "material_aliases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("materials.id", ondelete="CASCADE"))
    alias: Mapped[str] = mapped_column(String(255))


class AssistantQuestion(Base, TimestampMixin):
    __tablename__ = "assistant_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calculations.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    calculation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("calculations.id", ondelete="CASCADE"))
    revision_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("calculation_revisions.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[dict] = mapped_column(JSON)
    storage_key: Mapped[str | None] = mapped_column(String(1024), nullable=True)


class SyncEvent(Base):
    __tablename__ = "sync_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
