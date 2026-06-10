"""Схема БД по контрактам TZ-FINAL §4. Единственный источник правды по таблицам.
SQLAlchemy 2.0 declarative; типы совместимы с PostgreSQL и sqlite (тесты)."""
from datetime import datetime

from sqlalchemy import (
    JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(16), default="viewer")  # admin|viewer|user


class Session(Base, TimestampMixin):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(128), index=True)
    ip: Mapped[str | None] = mapped_column(String(45))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)


class Provider(Base, TimestampMixin):
    __tablename__ = "providers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    kind: Mapped[str] = mapped_column(String(16))  # local|external
    base_url: Mapped[str] = mapped_column(String(255))
    api_key_encrypted: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(128))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)


class ProductSet(Base, TimestampMixin):
    __tablename__ = "product_sets"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(255))


class Part(Base, TimestampMixin):
    __tablename__ = "parts"
    id: Mapped[int] = mapped_column(primary_key=True)
    designation: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    material: Mapped[str | None] = mapped_column(String(128))
    mass_kg: Mapped[float | None] = mapped_column(Float)
    extra: Mapped[dict | None] = mapped_column(JSON)
    __table_args__ = (UniqueConstraint("designation", name="uq_parts_designation"),)


class Geometry(Base, TimestampMixin):
    __tablename__ = "geometry"
    id: Mapped[int] = mapped_column(primary_key=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)
    volume_cm3: Mapped[float | None] = mapped_column(Float)
    bbox_mm: Mapped[list | None] = mapped_column(JSON)
    surfaces: Mapped[dict | None] = mapped_column(JSON)


class Notice(Base, TimestampMixin):
    __tablename__ = "notices"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(64), unique=True)
    date: Mapped[datetime | None] = mapped_column(DateTime)
    scan_object_key: Mapped[str | None] = mapped_column(String(255))
    affected: Mapped[list | None] = mapped_column(JSON)  # обозначения из извещения


class PartVersion(Base, TimestampMixin):
    __tablename__ = "part_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)
    product_set_id: Mapped[int] = mapped_column(ForeignKey("product_sets.id"), index=True)
    file_hash: Mapped[str] = mapped_column(String(64))
    source_path: Mapped[str] = mapped_column(String(512))
    doc_date: Mapped[datetime | None] = mapped_column(DateTime)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[str] = mapped_column(String(16), default="actual")  # actual|archive
    notice_id: Mapped[int | None] = mapped_column(ForeignKey("notices.id"))
    __table_args__ = (
        UniqueConstraint("part_id", "product_set_id", "file_hash", name="uq_part_version"),
    )


class WatchedDir(Base, TimestampMixin):
    __tablename__ = "watched_dirs"
    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(512), unique=True)
    product_set_id: Mapped[int] = mapped_column(ForeignKey("product_sets.id"))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_scan_at: Mapped[datetime | None] = mapped_column(DateTime)


class ScanRun(Base, TimestampMixin):
    __tablename__ = "scan_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    dir_id: Mapped[int] = mapped_column(ForeignKey("watched_dirs.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    files_seen: Mapped[int] = mapped_column(Integer, default=0)
    files_new: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="running")  # running|done|error


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # uuid
    status: Mapped[str] = mapped_column(String(16), default="queued")  # queued|running|done|error
    stage: Mapped[str | None] = mapped_column(String(64))
    part_id: Mapped[int | None] = mapped_column(ForeignKey("parts.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    rules_version: Mapped[int | None] = mapped_column(Integer)
    model_version: Mapped[str | None] = mapped_column(String(128))
    input_meta: Mapped[dict | None] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)


class NormRowDB(Base, TimestampMixin):
    __tablename__ = "norm_rows"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    num: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict] = mapped_column(JSON)  # NormRow.model_dump()


class Correction(Base, TimestampMixin):
    __tablename__ = "corrections"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    row_num: Mapped[int] = mapped_column(Integer)
    field: Mapped[str] = mapped_column(String(64))
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    stage: Mapped[str | None] = mapped_column(String(64))       # штамп|спецификация|символ...
    crop_object_key: Mapped[str | None] = mapped_column(String(255))
    model_version: Mapped[str | None] = mapped_column(String(128))
    rules_version: Mapped[int | None] = mapped_column(Integer)
    confirm_status: Mapped[str | None] = mapped_column(String(16))  # confirm|fix
    __table_args__ = (
        UniqueConstraint("job_id", "row_num", "field", "new_value", name="uq_correction"),
    )


class ModelUsage(Base, TimestampMixin):
    __tablename__ = "model_usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("providers.id"))
    model: Mapped[str] = mapped_column(String(128))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD


class Audit(Base, TimestampMixin):
    __tablename__ = "audit"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(128))
    details: Mapped[dict | None] = mapped_column(JSON)
