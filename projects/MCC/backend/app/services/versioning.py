"""Правило версий «актуальная/архив» (TZ-FINAL §4) — чистая логика без БД.
Cursor встраивает: применяет решение к part_versions в транзакции."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Decision(str, Enum):
    skip_duplicate = "skip_duplicate"          # hash уже есть в (part, set)
    first_actual = "first_actual"              # первая версия → actual
    supersede = "supersede"                    # новая actual, прежняя → archive
    incoming_archive = "incoming_archive"      # входящая старее актуальной → archive


@dataclass(frozen=True)
class VersionInfo:
    file_hash: str
    doc_date: datetime | None   # из штампа/извещения
    mtime: datetime             # фолбэк по §4


def _effective(v: VersionInfo) -> datetime:
    return v.doc_date or v.mtime


def resolve(
    incoming: VersionInfo,
    current_actual: VersionInfo | None,
    known_hashes: frozenset[str],
) -> Decision:
    """Решение по входящему файлу в рамках одного (part, product_set).
    То же обозначение в другом комплекте сюда не попадает — там своя независимая
    actual-версия (вызов с другим product_set)."""
    if incoming.file_hash in known_hashes:
        return Decision.skip_duplicate
    if current_actual is None:
        return Decision.first_actual
    if _effective(incoming) > _effective(current_actual):
        return Decision.supersede
    return Decision.incoming_archive
