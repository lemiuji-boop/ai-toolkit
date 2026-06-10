"""Загрузка и индексация документов из файлов (PDF, MD, JSON)."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.chunk import chunk_text
from app.core.config import settings
from app.core.schemas import Document, IngestRequest

logger = logging.getLogger(__name__)

# Поля rules.json, которые не несут нормативного смысла для RAG.
_RULES_SKIP_KEYS = {"_comment", "_zagotovki_comment", "_zagotovka_by_material_comment"}


def _log_path(path: Path) -> str:
    """SEC-002: в логах — только имя файла, не полный путь с обозначениями."""
    return path.name


def rules_json_to_text(data: dict) -> str:
    """Санitized текст из rules.json для индексации."""
    lines: list[str] = ["Правила расчёта норм расхода материалов (rules.json)."]
    if "kim_min" in data and "kim_max" in data:
        lines.append(f"Допустимый диапазон КИМ: {data['kim_min']} … {data['kim_max']}.")
    if z := data.get("zagotovki"):
        lines.append("Виды заготовки и коэффициенты:")
        for name, cfg in z.items():
            lines.append(
                f"  {name}: kr={cfg.get('kr')}, mz_factor_from_md={cfg.get('mz_factor_from_md')}."
            )
    if zm := data.get("zagotovka_by_material"):
        lines.append("Переопределение вида заготовки по марке материала:")
        for mat, kind in zm.items():
            lines.append(f"  {mat} → {kind}.")
    if dens := data.get("density"):
        lines.append("Плотности материалов (г/см³):")
        for mat, val in dens.items():
            lines.append(f"  {mat}: {val}.")
    return "\n".join(lines)


def extract_pdf_text(path: Path) -> str:
    import fitz  # pymupdf

    parts: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            parts.append(page.get_text("text"))
    return "\n".join(parts)


def load_file_documents(path: Path) -> list[Document]:
    """Извлекает чанки из одного файла."""
    suffix = path.suffix.lower()
    source_label = f"file:{path.name}"

    if suffix == ".json" and path.name == "rules.json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        filtered = {k: v for k, v in raw.items() if k not in _RULES_SKIP_KEYS}
        text = rules_json_to_text(filtered)
        source_label = "backend/app/data/rules.json"
    elif suffix == ".json":
        raw_json = json.loads(path.read_text(encoding="utf-8"))
        text = json.dumps(raw_json, ensure_ascii=False, indent=2)
    elif suffix in {".md", ".txt"}:
        text = path.read_text(encoding="utf-8")
    elif suffix == ".pdf":
        text = extract_pdf_text(path)
        source_label = f"pdf:{path.name}"
    else:
        logger.debug("Пропуск неподдерживаемого формата: %s", _log_path(path))
        return []

    return chunk_text(
        text,
        source=source_label,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )


def collect_paths(req: IngestRequest) -> list[Path]:
    """Собирает список файлов для ingest."""
    root = Path(settings.project_root)
    paths: list[Path] = []

    if req.paths:
        for p in req.paths:
            fp = Path(p)
            if not fp.is_absolute():
                fp = root / fp
            if fp.is_file():
                paths.append(fp)
            elif fp.is_dir():
                paths.extend(sorted(fp.rglob("*")))
    elif req.use_default_corpus:
        for rel in settings.corpus_paths:
            fp = root / rel
            if fp.is_file():
                paths.append(fp)
            elif fp.is_dir():
                paths.extend(sorted(fp.glob("*.md")))
                paths.extend(sorted(fp.glob("*.txt")))
                paths.extend(sorted(fp.glob("*.pdf")))

    # Только поддерживаемые расширения.
    allowed = {".pdf", ".md", ".txt", ".json"}
    return [p for p in paths if p.is_file() and p.suffix.lower() in allowed]


def ingest_files(req: IngestRequest) -> tuple[list[Document], list[str]]:
    """Читает файлы, возвращает документы и список обработанных имён (без содержимого)."""
    files = collect_paths(req)
    all_docs: list[Document] = []
    processed: list[str] = []
    seen_ids: set[str] = set()

    for fp in files:
        try:
            docs = load_file_documents(fp)
        except Exception as exc:
            logger.warning("Ошибка ingest %s: %s", _log_path(fp), type(exc).__name__)
            continue
        for d in docs:
            if d.id not in seen_ids:
                seen_ids.add(d.id)
                all_docs.append(d)
        if docs:
            processed.append(fp.name)

    return all_docs, processed
