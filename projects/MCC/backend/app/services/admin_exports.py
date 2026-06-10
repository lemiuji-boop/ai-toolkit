"""Список экспортов и прогресс пакетных заданий для админ-панели (SEC-002)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from app.services import job_store

# Только hex-идентификаторы в jobs/ — без обозначений изделий
_JOB_FILE_RE = re.compile(r"^[a-f0-9]{12}\.json$")

# Разрешённые относительные пути внутри data/exports/
_STATIC_EXPORTS = frozenset(
    {
        "report_summary.json",
        "report_summary.md",
        "reports/material_norms.csv",
    }
)

_REF_XLSX_RE = re.compile(r"^ref_[a-f0-9]{12}\.xlsx$")


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def exports_dir() -> Path:
    override = os.environ.get("MATNORM_EXPORTS_DIR")
    if override:
        return Path(override)
    return _project_root() / "data" / "exports"


def tunnel_url_file() -> Path:
    override = os.environ.get("MATNORM_TUNNEL_URL_FILE")
    if override:
        return Path(override)
    return _project_root() / ".tunnel-url"


def read_tunnel_url() -> str | None:
    """Публичный URL Cloudflare tunnel из .tunnel-url (если файл есть)."""
    path = tunnel_url_file()
    if not path.is_file():
        return None
    url = path.read_text(encoding="utf-8").strip()
    return url or None


def addin_zip_path() -> Path:
    return _project_root() / "addin" / "matnorm-addin.zip"


def _is_allowed_export(rel: str) -> bool:
    if rel in _STATIC_EXPORTS:
        return True
    if rel.startswith("jobs/"):
        name = Path(rel).name
        return bool(_JOB_FILE_RE.match(name))
    if rel.startswith("reports/") and rel.endswith("_summary.json"):
        # Агрегаты по file_id (хеш), без обозначений в имени файла
        stem = Path(rel).stem.replace("_summary", "")
        return bool(re.fullmatch(r"[a-f0-9]{12}", stem))
    if rel.startswith("reports/"):
        name = Path(rel).name
        if name == "material_norms.csv":
            return True
        if _REF_XLSX_RE.match(name):
            return True
    return False


def resolve_export_path(rel: str) -> Path | None:
    """Безопасное разрешение пути: только под data/exports/, без traversal."""
    rel = rel.replace("\\", "/").lstrip("/")
    if not rel or ".." in rel.split("/"):
        return None
    if not _is_allowed_export(rel):
        return None
    root = exports_dir().resolve()
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    if not target.is_file():
        return None
    return target


def collect_progress() -> dict:
    """Прогресс экспорта: report_summary.json или журнал job_store."""
    summary_path = exports_dir() / "report_summary.json"
    if summary_path.is_file():
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            stats = payload.get("stats") or {}
            total = int(stats.get("jobs_total", 0))
            failed = int(stats.get("jobs_failed", 0))
            completed = int(stats.get("jobs_ok", max(total - failed, 0)))
            in_progress = max(total - completed - failed, 0)
            percent = round((completed / total) * 100, 1) if total else 0.0
            return {
                "total": total,
                "completed": completed,
                "failed": failed,
                "in_progress": in_progress,
                "percent": percent,
                "source": "report_summary",
            }
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            pass

    job_store.load_persisted()
    jobs = job_store.list_jobs(limit=50)
    total = len(jobs)
    failed = sum(1 for j in jobs if j.get("status") == "failed")
    completed = sum(1 for j in jobs if j.get("status") == "completed")
    in_progress = sum(1 for j in jobs if j.get("status") not in ("completed", "failed"))
    percent = round((completed / total) * 100, 1) if total else 0.0
    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "in_progress": in_progress,
        "percent": percent,
        "source": "job_store",
    }


def list_export_files() -> list[dict]:
    """Список готовых файлов экспорта (без конфиденциальных имён)."""
    root = exports_dir()
    if not root.is_dir():
        return []

    files: list[dict] = []
    labels = {
        "report_summary.json": "Сводка экспорта (JSON)",
        "report_summary.md": "Сводка экспорта (Markdown)",
        "reports/material_norms.csv": "Нормы материалов (CSV)",
    }

    for rel in sorted(_STATIC_EXPORTS):
        path = root / rel
        if path.is_file():
            files.append(
                {
                    "path": rel,
                    "label": labels.get(rel, rel),
                    "size_bytes": path.stat().st_size,
                    "category": "report",
                }
            )

    jobs_dir = root / "jobs"
    if jobs_dir.is_dir():
        for path in sorted(jobs_dir.glob("*.json")):
            if not _JOB_FILE_RE.match(path.name):
                continue
            rel = f"jobs/{path.name}"
            files.append(
                {
                    "path": rel,
                    "label": f"Задание {path.stem[:8]}…",
                    "size_bytes": path.stat().st_size,
                    "category": "job",
                }
            )

    return files


def job_export_count() -> int:
    jobs_dir = exports_dir() / "jobs"
    if not jobs_dir.is_dir():
        return 0
    return sum(1 for p in jobs_dir.glob("*.json") if _JOB_FILE_RE.match(p.name))


def _read_job_meta(path: Path) -> dict:
    """Метаданные задания без обозначений (SEC-002)."""
    job_hash = path.stem
    meta: dict = {
        "job_hash": job_hash,
        "mode": None,
        "verify_ok": None,
        "rows_count": None,
        "extract_source": None,
        "geometry_source": None,
    }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return meta
    meta["mode"] = payload.get("mode")
    verify = payload.get("verify") or {}
    meta["verify_ok"] = verify.get("ok")
    rows = payload.get("rows") or []
    meta["rows_count"] = len(rows)
    extract = payload.get("extract") or {}
    geometry = payload.get("geometry") or {}
    meta["extract_source"] = extract.get("source")
    meta["geometry_source"] = geometry.get("source")
    return meta


def _sanitize_row(row: dict) -> dict:
    """Строка ведомости без конфиденциальных полей."""
    return {
        "num": row.get("num"),
        "material": row.get("material"),
        "zagotovka": row.get("zagotovka"),
        "qty_per_set": row.get("qty_per_set"),
        "md_kg": row.get("md_kg"),
        "mz_kg": row.get("mz_kg"),
        "kim": row.get("kim"),
        "norm_per_part_kg": row.get("norm_per_part_kg"),
        "norm_program_kg": row.get("norm_program_kg"),
        "flags": row.get("flags") or [],
    }


def sanitize_job_payload(payload: dict) -> dict:
    """Результат расчёта для надстройки Excel — без обозначений и наименований."""
    verify = payload.get("verify") or {}
    extract = payload.get("extract") or {}
    geometry = payload.get("geometry") or {}
    return {
        "job_id": payload.get("job_id"),
        "job_hash": payload.get("job_hash"),
        "mode": payload.get("mode"),
        "data_completeness": payload.get("data_completeness"),
        "extract": {
            "material": extract.get("material"),
            "mass_kg": extract.get("mass_kg"),
            "source": extract.get("source"),
        },
        "geometry": {
            "volume_cm3": geometry.get("volume_cm3"),
            "mass_kg": geometry.get("mass_kg"),
            "source": geometry.get("source"),
            "is_assembly": geometry.get("is_assembly"),
        },
        "verify": {"ok": verify.get("ok"), "flags": verify.get("flags") or []},
        "rows": [_sanitize_row(r) for r in (payload.get("rows") or [])],
    }


def fetch_job_by_hash(job_hash: str) -> dict | None:
    """Загрузка и санитизация результата задания по 12-символьному хешу."""
    if not re.fullmatch(r"[a-f0-9]{12}", job_hash):
        return None
    rel = f"jobs/{job_hash}.json"
    path = resolve_export_path(rel)
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    payload["job_hash"] = job_hash
    return sanitize_job_payload(payload)


def list_addin_catalog() -> dict:
    """Каталог готовых данных для надстройки Excel (без обозначений изделий)."""
    root = exports_dir()
    reports: list[dict] = []
    jobs: list[dict] = []
    reference: list[dict] = []

    labels = {
        "report_summary.json": "Сводка экспорта (JSON)",
        "report_summary.md": "Сводка экспорта (Markdown)",
        "reports/material_norms.csv": "Нормы материалов (CSV)",
    }

    for rel in sorted(_STATIC_EXPORTS):
        path = root / rel
        if not path.is_file():
            continue
        reports.append(
            {
                "path": rel,
                "label": labels.get(rel, rel),
                "size_bytes": path.stat().st_size,
                "download_url": f"/api/addin/download?path={rel}",
            }
        )

    reports_dir = root / "reports"
    if reports_dir.is_dir():
        for path in sorted(reports_dir.glob("*_summary.json")):
            stem = path.stem.replace("_summary", "")
            if not re.fullmatch(r"[a-f0-9]{12}", stem):
                continue
            rel = f"reports/{path.name}"
            try:
                summary = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                summary = {}
            reports.append(
                {
                    "path": rel,
                    "label": f"Сводка задания {stem[:8]}…",
                    "size_bytes": path.stat().st_size,
                    "job_hash": stem,
                    "mode": summary.get("mode"),
                    "verify_ok": summary.get("verify_ok"),
                    "rows_count": summary.get("rows_count"),
                    "download_url": f"/api/addin/download?path={rel}",
                }
            )
        for path in sorted(reports_dir.glob("ref_*.xlsx")):
            if not _REF_XLSX_RE.match(path.name):
                continue
            rel = f"reports/{path.name}"
            reference.append(
                {
                    "path": rel,
                    "label": f"Эталон {path.stem[4:12]}…",
                    "size_bytes": path.stat().st_size,
                    "download_url": f"/api/addin/download?path={rel}",
                }
            )

    jobs_dir = root / "jobs"
    if jobs_dir.is_dir():
        for path in sorted(jobs_dir.glob("*.json")):
            if not _JOB_FILE_RE.match(path.name):
                continue
            rel = f"jobs/{path.name}"
            meta = _read_job_meta(path)
            jobs.append(
                {
                    "path": rel,
                    "label": f"Задание {meta['job_hash'][:8]}…",
                    "size_bytes": path.stat().st_size,
                    "download_url": f"/api/addin/download?path={rel}",
                    **meta,
                }
            )

    return {
        "groups": {
            "reports": reports,
            "jobs": jobs,
            "reference": reference,
        },
        "total": len(reports) + len(jobs) + len(reference),
        "job_count": len(jobs),
    }
