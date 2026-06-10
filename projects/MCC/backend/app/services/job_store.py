"""Хранилище последних заданий для админ-панели (без ПДн/обозначений).

Кольцевой буфер в памяти + журнал data/admin/jobs.jsonl.
При пустом журнале — импорт из data/exports/jobs/*.json (история экспорта).
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

from app.core.schemas import JobResult

_MAX_JOBS = 50

_lock = Lock()
_jobs: deque[dict] = deque(maxlen=_MAX_JOBS)
_loaded = False


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _jobs_file() -> Path:
    override = os.environ.get("MATNORM_ADMIN_JOBS_PATH")
    if override:
        return Path(override)
    return _project_root() / "data" / "admin" / "jobs.jsonl"


def _exports_jobs_dir() -> Path:
    override = os.environ.get("MATNORM_EXPORTS_JOBS_DIR")
    if override:
        return Path(override)
    return _project_root() / "data" / "exports" / "jobs"


def _input_hash(drawing_bytes: bytes, model_bytes: bytes) -> str:
    """Хеш входных файлов без сохранения имён и содержимого (SEC-002)."""
    h = hashlib.sha256()
    h.update(drawing_bytes)
    h.update(model_bytes)
    return h.hexdigest()[:16]


def _record_from_result(
    result: JobResult,
    *,
    drawing_bytes: bytes = b"",
    model_bytes: bytes = b"",
    status: str = "completed",
) -> dict:
    now = datetime.now(UTC)
    return {
        "job_id": result.job_id,
        "input_hash": _input_hash(drawing_bytes, model_bytes),
        "mode": result.mode,
        "status": status,
        "data_completeness": result.data_completeness.model_dump(),
        "vision_available": result.extract.source == "llm",
        "geometry_available": result.geometry.source == "cad",
        "verify_ok": result.verify.ok,
        "flags_count": len(result.verify.flags),
        "rows_count": len(result.rows),
        "started_at": now.isoformat(),
        "finished_at": now.isoformat(),
        "source": "api",
    }


def _record_from_export(payload: dict, *, file_id: str = "") -> dict | None:
    """Преобразовать JSON экспорта в запись админ-журнала (без обозначений в полях)."""
    job_id = payload.get("job_id")
    if not job_id:
        return None
    ex = payload.get("extract") or {}
    geom = payload.get("geometry") or {}
    now = datetime.now(UTC).isoformat()
    ih = file_id[:16] if file_id else hashlib.sha256(str(job_id).encode()).hexdigest()[:16]
    return {
        "job_id": job_id,
        "input_hash": ih,
        "mode": payload.get("mode", "paired"),
        "status": "completed",
        "data_completeness": payload.get("data_completeness") or {},
        "vision_available": ex.get("source") == "llm",
        "geometry_available": geom.get("source") == "cad",
        "verify_ok": (payload.get("verify") or {}).get("ok"),
        "flags_count": len((payload.get("verify") or {}).get("flags") or []),
        "rows_count": len(payload.get("rows") or []),
        "started_at": payload.get("started_at", now),
        "finished_at": payload.get("finished_at", now),
        "source": "export",
    }


def _append_persisted(record: dict) -> None:
    path = _jobs_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_persisted() -> int:
    """Загрузить журнал с диска; при пустом — импорт из data/exports/jobs/."""
    global _loaded
    with _lock:
        if _loaded:
            return len(_jobs)
        _loaded = True

    count = _load_jsonl()
    if count == 0:
        count = _import_exports()
    return count


def _load_jsonl() -> int:
    path = _jobs_file()
    if not path.is_file():
        return 0
    loaded: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            loaded.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    tail = loaded[-_MAX_JOBS:]
    with _lock:
        for rec in reversed(tail):
            _jobs.appendleft(rec)
    return len(tail)


def _import_exports() -> int:
    exports_dir = _exports_jobs_dir()
    if not exports_dir.is_dir():
        return 0
    records: list[dict] = []
    for path in sorted(exports_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        rec = _record_from_export(payload, file_id=path.stem)
        if rec:
            records.append(rec)
    if not records:
        return 0

    tail = records[-_MAX_JOBS:]
    jobs_file = _jobs_file()
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    with jobs_file.open("w", encoding="utf-8") as f:
        for rec in tail:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with _lock:
        for rec in reversed(tail):
            _jobs.appendleft(rec)
    return len(tail)


def register_job(
    result: JobResult,
    *,
    drawing_bytes: bytes = b"",
    model_bytes: bytes = b"",
    status: str = "completed",
) -> None:
    """Добавить запись о завершённом задании в буфер и на диск."""
    record = _record_from_result(
        result,
        drawing_bytes=drawing_bytes,
        model_bytes=model_bytes,
        status=status,
    )
    with _lock:
        _jobs.appendleft(record)
    _append_persisted(record)


def list_jobs(limit: int = 50) -> list[dict]:
    """Список последних заданий (новые первыми)."""
    with _lock:
        return list(_jobs)[:limit]


def active_jobs_count() -> int:
    """Количество заданий в буфере (все завершённые; активных нет в stateless API)."""
    with _lock:
        return len(_jobs)


def reset_for_tests() -> None:
    """Сброс состояния (только для unit-тестов)."""
    global _loaded
    with _lock:
        _jobs.clear()
        _loaded = False
