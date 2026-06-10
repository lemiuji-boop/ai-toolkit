#!/usr/bin/env python3
"""Пакетный экспорт и анализ КД через POST /api/jobs.

Сохраняет JSON-результаты, деревья сборки и сводку материалов в data/exports/.
Имена файлов — только хеши (SEC-002); обозначения остаются внутри JSON для ручного анализа.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

# Расширения входных файлов
DRAWING_EXTS = {".pdf", ".png", ".jpg", ".jpeg"}
MODEL_EXTS = {".step", ".stp"}
REF_EXTS = {".xlsx", ".xls"}


def _sha12(text: str) -> str:
    """Короткий хеш для имён файлов (SEC-002)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _basename_key(path: Path) -> str:
    return path.stem.lower()


@dataclass
class JobSpec:
    """Описание одного задания конвейера."""

    mode: str
    drawing: Path | None
    model: Path | None
    file_id: str  # хеш идентификатора (без обозначения в имени)


@dataclass
class JobOutcome:
    spec: JobSpec
    ok: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    elapsed_s: float = 0.0


@dataclass
class ExportSummary:
    """Сводка прогона для report_summary."""

    started_at: str
    source_folder: str
    backend_url: str
    workers: int
    jobs_total: int = 0
    jobs_ok: int = 0
    jobs_failed: int = 0
    paired: int = 0
    drawing_only: int = 0
    model_only: int = 0
    vision_llm: int = 0
    vision_stub: int = 0
    geometry_cad: int = 0
    geometry_stub: int = 0
    trees_built: int = 0
    total_norm_program_kg: float = 0.0
    material_totals: dict[str, float] = field(default_factory=dict)
    failures: list[dict[str, str]] = field(default_factory=list)
    job_index: list[dict[str, Any]] = field(default_factory=list)


def discover_jobs(folder: Path) -> list[JobSpec]:
    """Автодетект пар и одиночных файлов (как ingest-folder.sh)."""
    drawings = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in DRAWING_EXTS
    )
    models = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in MODEL_EXTS
    )
    draw_by_key = {_basename_key(p): p for p in drawings}
    model_by_key = {_basename_key(p): p for p in models}

    specs: list[JobSpec] = []
    paired_keys = set(draw_by_key) & set(model_by_key)
    for key in sorted(paired_keys):
        d, m = draw_by_key[key], model_by_key[key]
        specs.append(JobSpec("paired", d, m, _sha12(f"{d.name}|{m.name}")))
    for key in sorted(set(draw_by_key) - paired_keys):
        d = draw_by_key[key]
        specs.append(JobSpec("drawing_only", d, None, _sha12(d.name)))
    for key in sorted(set(model_by_key) - paired_keys):
        m = model_by_key[key]
        specs.append(JobSpec("model_only", None, m, _sha12(m.name)))
    return specs


def _run_single_job(
    backend_url: str,
    spec: JobSpec,
    timeout: float,
    retries: int = 3,
) -> JobOutcome:
    """Отправка одного задания на бэкенд с повторами при сетевых сбоях."""
    url = f"{backend_url.rstrip('/')}/api/jobs?mode={spec.mode}"
    files_payload: dict[str, tuple[str, bytes, str]] = {}
    if spec.drawing is not None:
        raw = spec.drawing.read_bytes()
        files_payload["drawing"] = (
            spec.drawing.name,
            raw,
            "application/octet-stream",
        )
    if spec.model is not None:
        raw = spec.model.read_bytes()
        files_payload["model3d"] = (
            spec.model.name,
            raw,
            "application/octet-stream",
        )
    t0 = time.monotonic()
    last_err = "unknown"
    for attempt in range(1, retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(url, files=files_payload)
                resp.raise_for_status()
                data = resp.json()
            return JobOutcome(spec, True, data, elapsed_s=time.monotonic() - t0)
        except Exception as exc:  # noqa: BLE001
            last_err = str(exc)
            if attempt < retries:
                time.sleep(min(2.0 * attempt, 10.0))
    return JobOutcome(
        spec, False, error=last_err, elapsed_s=time.monotonic() - t0
    )


def _tree_summary(node: dict[str, Any] | None) -> dict[str, Any] | None:
    """Компактное дерево для отчёта (входимость / узлы)."""
    if node is None:
        return None

    def walk(n: dict[str, Any]) -> dict[str, Any]:
        return {
            "designation": n.get("designation"),
            "name": n.get("name"),
            "material": n.get("material"),
            "qty": n.get("qty", 1),
            "mass_kg": n.get("mass_kg"),
            "children": [walk(c) for c in n.get("children") or []],
        }

    return walk(node)


def _job_summary(result: dict[str, Any]) -> dict[str, Any]:
    """Краткая сводка по заданию (без полного debug)."""
    rows = result.get("rows") or []
    geom = result.get("geometry") or {}
    ex = result.get("extract") or {}
    return {
        "job_id": result.get("job_id"),
        "mode": result.get("mode"),
        "data_completeness": result.get("data_completeness"),
        "extract_source": ex.get("source"),
        "geometry_source": geom.get("source"),
        "is_assembly": geom.get("is_assembly"),
        "verify_ok": (result.get("verify") or {}).get("ok"),
        "verify_flags_count": len((result.get("verify") or {}).get("flags") or []),
        "rows_count": len(rows),
        "assembly_tree": _tree_summary(geom.get("assembly_tree")),
        "material_norms": [
            {
                "num": r.get("num"),
                "designation": r.get("designation"),
                "material": r.get("material"),
                "qty_per_set": r.get("qty_per_set"),
                "md_kg": r.get("md_kg"),
                "norm_program_kg": r.get("norm_program_kg"),
                "kim": r.get("kim"),
            }
            for r in rows
        ],
        "totals": {
            "norm_program_kg": round(
                sum(r.get("norm_program_kg") or 0.0 for r in rows), 4
            ),
        },
    }


def _ensure_dirs(exports_root: Path) -> dict[str, Path]:
    sub = ("drawings", "models", "reports", "jobs")
    out: dict[str, Path] = {}
    for name in sub:
        p = exports_root / name
        p.mkdir(parents=True, exist_ok=True)
        out[name] = p
    return out


def _copy_reference_files(source: Path, reports_dir: Path) -> list[str]:
    copied: list[str] = []
    for p in sorted(source.iterdir()):
        if p.is_file() and p.suffix.lower() in REF_EXTS:
            dest = reports_dir / f"ref_{_sha12(p.name)}.xlsx"
            dest.write_bytes(p.read_bytes())
            copied.append(dest.name)
    return copied


def _write_csv_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _render_md(summary: ExportSummary) -> str:
    lines = [
        "# Сводка экспорта МАТНОРМ",
        "",
        f"- **Начало:** {summary.started_at}",
        f"- **Источник:** `{summary.source_folder}`",
        f"- **Backend:** {summary.backend_url}",
        f"- **Workers:** {summary.workers}",
        "",
        "## Задания",
        "",
        f"| Метрика | Значение |",
        f"|---|---|",
        f"| Всего | {summary.jobs_total} |",
        f"| Успешно | {summary.jobs_ok} |",
        f"| Ошибки | {summary.jobs_failed} |",
        f"| paired | {summary.paired} |",
        f"| drawing_only | {summary.drawing_only} |",
        f"| model_only | {summary.model_only} |",
        "",
        "## Источники данных",
        "",
        f"- Vision LLM: {summary.vision_llm}, stub: {summary.vision_stub}",
        f"- Geometry CAD: {summary.geometry_cad}, stub: {summary.geometry_stub}",
        f"- Деревьев сборки: {summary.trees_built}",
        "",
        "## Материалы (норма на программу, кг)",
        "",
    ]
    if summary.material_totals:
        lines.append("| Материал | Σ norm_program_kg |")
        lines.append("|---|---|")
        for mat, val in sorted(summary.material_totals.items()):
            lines.append(f"| {mat or '(не указан)'} | {val:.4f} |")
    else:
        lines.append("_Нет данных_")
    lines.extend(
        [
            "",
            f"**Итого norm_program_kg:** {summary.total_norm_program_kg:.4f} кг",
            "",
        ]
    )
    if summary.failures:
        lines.append("## Ошибки")
        lines.append("")
        for f in summary.failures:
            lines.append(f"- `{f['file_id']}`: {f['error']}")
    lines.append("")
    lines.append("## Индекс заданий")
    lines.append("")
    lines.append("| file_id | mode | extract | geometry | rows |")
    lines.append("|---|---|---|---|---|")
    for j in summary.job_index:
        lines.append(
            f"| {j['file_id']} | {j['mode']} | {j.get('extract_source')} | "
            f"{j.get('geometry_source')} | {j.get('rows_count')} |"
        )
    return "\n".join(lines) + "\n"


def run_export(
    source_folder: Path,
    exports_root: Path,
    backend_url: str,
    workers: int,
    timeout: float,
) -> ExportSummary:
    """Основной прогон: задания → экспорт → сводка."""
    started = datetime.now(UTC).isoformat()
    dirs = _ensure_dirs(exports_root)
    ref_files = _copy_reference_files(source_folder, dirs["reports"])

    if not httpx.get(f"{backend_url.rstrip('/')}/health", timeout=5.0).is_success:
        raise RuntimeError(f"Backend недоступен: {backend_url}")

    specs = discover_jobs(source_folder)
    summary = ExportSummary(
        started_at=started,
        source_folder=str(source_folder),
        backend_url=backend_url,
        workers=workers,
        jobs_total=len(specs),
    )

    outcomes: list[JobOutcome] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {
            pool.submit(_run_single_job, backend_url, spec, timeout): spec
            for spec in specs
        }
        for fut in as_completed(futures):
            outcomes.append(fut.result())

    csv_rows: list[dict[str, Any]] = []

    for outcome in sorted(outcomes, key=lambda o: o.spec.file_id):
        spec = outcome.spec
        if not outcome.ok or outcome.result is None:
            summary.jobs_failed += 1
            summary.failures.append({"file_id": spec.file_id, "error": outcome.error or "unknown"})
            continue

        summary.jobs_ok += 1
        result = outcome.result
        mode = result.get("mode", spec.mode)
        if mode == "paired":
            summary.paired += 1
        elif mode == "drawing_only":
            summary.drawing_only += 1
        else:
            summary.model_only += 1

        ex = result.get("extract") or {}
        geom = result.get("geometry") or {}
        if ex.get("source") == "llm":
            summary.vision_llm += 1
        else:
            summary.vision_stub += 1
        if geom.get("source") == "cad":
            summary.geometry_cad += 1
        else:
            summary.geometry_stub += 1
        if geom.get("is_assembly") and geom.get("assembly_tree"):
            summary.trees_built += 1

        # Полный JSON
        job_path = dirs["jobs"] / f"{spec.file_id}.json"
        job_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        brief = _job_summary(result)
        brief_path = dirs["reports"] / f"{spec.file_id}_summary.json"
        brief_path.write_text(
            json.dumps(brief, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        if spec.drawing is not None:
            draw_meta = dirs["drawings"] / f"{spec.file_id}.json"
            draw_meta.write_text(
                json.dumps(
                    {
                        "file_id": spec.file_id,
                        "mode": mode,
                        "extract": ex,
                        "verify": result.get("verify"),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        if spec.model is not None:
            model_meta = dirs["models"] / f"{spec.file_id}.json"
            model_meta.write_text(
                json.dumps(
                    {
                        "file_id": spec.file_id,
                        "mode": mode,
                        "geometry": geom,
                        "assembly_tree": geom.get("assembly_tree"),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

        for row in result.get("rows") or []:
            mat = row.get("material") or ""
            norm = row.get("norm_program_kg") or 0.0
            summary.material_totals[mat] = summary.material_totals.get(mat, 0.0) + norm
            summary.total_norm_program_kg += norm
            csv_rows.append(
                {
                    "file_id": spec.file_id,
                    "mode": mode,
                    "designation": row.get("designation"),
                    "material": row.get("material"),
                    "qty_per_set": row.get("qty_per_set"),
                    "md_kg": row.get("md_kg"),
                    "norm_program_kg": row.get("norm_program_kg"),
                    "kim": row.get("kim"),
                }
            )

        summary.job_index.append(
            {
                "file_id": spec.file_id,
                "mode": mode,
                "extract_source": ex.get("source"),
                "geometry_source": geom.get("source"),
                "rows_count": len(result.get("rows") or []),
                "elapsed_s": round(outcome.elapsed_s, 2),
            }
        )

    summary.total_norm_program_kg = round(summary.total_norm_program_kg, 4)
    summary.material_totals = {
        k: round(v, 4) for k, v in summary.material_totals.items()
    }

    report_json = {
        "started_at": summary.started_at,
        "source_folder": summary.source_folder,
        "backend_url": summary.backend_url,
        "workers": summary.workers,
        "reference_xlsx": ref_files,
        "jobs": summary.job_index,
        "stats": {
            "jobs_total": summary.jobs_total,
            "jobs_ok": summary.jobs_ok,
            "jobs_failed": summary.jobs_failed,
            "paired": summary.paired,
            "drawing_only": summary.drawing_only,
            "model_only": summary.model_only,
            "vision_llm": summary.vision_llm,
            "vision_stub": summary.vision_stub,
            "geometry_cad": summary.geometry_cad,
            "geometry_stub": summary.geometry_stub,
            "trees_built": summary.trees_built,
            "total_norm_program_kg": summary.total_norm_program_kg,
            "material_totals": summary.material_totals,
        },
        "failures": summary.failures,
    }
    (exports_root / "report_summary.json").write_text(
        json.dumps(report_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (exports_root / "report_summary.md").write_text(
        _render_md(summary), encoding="utf-8"
    )
    _write_csv_summary(exports_root / "reports" / "material_norms.csv", csv_rows)

    return summary


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Экспорт и анализ КД через /api/jobs")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(os.environ.get("SOURCE_FOLDER", "/media/data/work/MCC")),
        help="Папка с PDF/STEP/XLSX",
    )
    parser.add_argument(
        "--exports",
        type=Path,
        default=root / "data" / "exports",
        help="Каталог экспорта",
    )
    parser.add_argument(
        "--backend",
        default=os.environ.get("BACKEND_URL", "http://127.0.0.1:8123"),
        help="URL бэкенда",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.environ.get("EXPORT_WORKERS", min(4, os.cpu_count() or 2))),
        help="Параллельные задания",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("EXPORT_TIMEOUT", "600")),
        help="Таймаут одного задания, сек",
    )
    args = parser.parse_args()

    if not args.source.is_dir():
        print(f"Ошибка: папка не найдена: {args.source}", file=sys.stderr)
        return 1

    print(f"→ источник: {args.source}")
    print(f"→ экспорт:  {args.exports}")
    print(f"→ backend:  {args.backend}")
    print(f"→ workers:  {args.workers}")

    try:
        summary = run_export(
            args.source, args.exports, args.backend, args.workers, args.timeout
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1

    print("--- сводка ---")
    print(f"jobs: {summary.jobs_ok}/{summary.jobs_total} ok, failed={summary.jobs_failed}")
    print(f"trees: {summary.trees_built}, norm_total={summary.total_norm_program_kg} kg")
    print(f"→ {args.exports / 'report_summary.json'}")
    return 0 if summary.jobs_failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
