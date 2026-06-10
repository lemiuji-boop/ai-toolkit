"""Чанкинг русскоязычных технических документов (ГОСТ/ОСТ/ТУ, markdown)."""
from __future__ import annotations

import hashlib
import re

from app.core.schemas import Document

# Разделители абзацев и заголовков markdown.
_PARA_SPLIT = re.compile(r"\n\s*\n+")
_HEADER_RE = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)
# Границы предложений для кириллицы и латиницы.
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?;])\s+(?=[А-ЯA-Z0-9«\"(])")


def _doc_id(source: str, index: int, text: str) -> str:
    h = hashlib.sha256(f"{source}:{index}:{text[:64]}".encode()).hexdigest()[:16]
    return f"{source}#{index}:{h}"


def _split_sentences(text: str) -> list[str]:
    parts = _SENTENCE_SPLIT.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def _pack_units(units: list[str], chunk_size: int) -> list[str]:
    """Склеивает мелкие абзацы до chunk_size."""
    chunks: list[str] = []
    buf = ""
    for unit in units:
        if not unit:
            continue
        candidate = f"{buf}\n\n{unit}".strip() if buf else unit
        if len(candidate) <= chunk_size:
            buf = candidate
        else:
            if buf:
                chunks.append(buf)
            if len(unit) <= chunk_size:
                buf = unit
            else:
                # Длинный абзац — режем по предложениям.
                for sent in _split_sentences(unit):
                    if len(sent) <= chunk_size:
                        can_merge = buf and len(buf) + len(sent) + 1 <= chunk_size
                        sub = f"{buf} {sent}".strip() if can_merge else sent
                        if len(sub) <= chunk_size and buf:
                            buf = sub
                        elif buf:
                            chunks.append(buf)
                            buf = sent if len(sent) <= chunk_size else ""
                            if len(sent) > chunk_size:
                                for i in range(0, len(sent), chunk_size):
                                    chunks.append(sent[i : i + chunk_size])
                        else:
                            if len(sent) > chunk_size:
                                for i in range(0, len(sent), chunk_size):
                                    chunks.append(sent[i : i + chunk_size])
                            else:
                                buf = sent
                    else:
                        if buf:
                            chunks.append(buf)
                            buf = ""
                        for i in range(0, len(sent), chunk_size):
                            chunks.append(sent[i : i + chunk_size])
    if buf:
        chunks.append(buf)
    return chunks


def _apply_overlap(chunks: list[str], overlap: int) -> list[str]:
    if overlap <= 0 or len(chunks) <= 1:
        return chunks
    out: list[str] = []
    prev_tail = ""
    for chunk in chunks:
        merged = f"{prev_tail} {chunk}".strip() if prev_tail else chunk
        out.append(merged)
        prev_tail = chunk[-overlap:] if len(chunk) > overlap else chunk
    return out


def chunk_text(
    text: str,
    *,
    source: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[Document]:
    """Разбивает текст на чанки с перекрытием; source — цитирование (FR-003)."""
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    # Сохраняем заголовки секций как отдельные единицы для лучшего контекста.
    units: list[str] = []
    last = 0
    for m in _HEADER_RE.finditer(normalized):
        if m.start() > last:
            block = normalized[last : m.start()].strip()
            if block:
                units.extend(p.strip() for p in _PARA_SPLIT.split(block) if p.strip())
        units.append(m.group(1).strip())
        last = m.end()
    tail = normalized[last:].strip()
    if tail:
        units.extend(p.strip() for p in _PARA_SPLIT.split(tail) if p.strip())

    raw_chunks = _pack_units(units, chunk_size)
    overlapped = _apply_overlap(raw_chunks, overlap)

    docs: list[Document] = []
    for i, chunk in enumerate(overlapped):
        docs.append(
            Document(
                id=_doc_id(source, i, chunk),
                text=chunk,
                source=source,
            )
        )
    return docs
