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

"""Проверка путей файлов: только внутри разрешённых корней хранилища."""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings


def allowed_roots() -> list[Path]:
    roots: list[Path] = []
    for raw in (settings.file_storage_root, settings.catalog_root):
        if raw:
            roots.append(Path(raw).resolve())
    return roots


def resolve_allowed_path(file_path: str, *, must_exist: bool = True) -> Path:
    """Возвращает нормализованный путь или 403, если выход за пределы storage/catalog."""
    try:
        resolved = Path(file_path).resolve()
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path") from exc

    for root in allowed_roots():
        try:
            resolved.relative_to(root)
            if must_exist and not resolved.is_file():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
            return resolved
        except ValueError:
            continue

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Path outside allowed storage")


def safe_upload_filename(filename: str | None) -> str:
    """Имя файла без каталогов и опасных символов."""
    import re

    base = Path(filename or "document.pdf").name
    base = re.sub(r"[^\w.\-]", "_", base, flags=re.UNICODE)
    if not base.lower().endswith(".pdf"):
        base = f"{base}.pdf"
    return base[:200]
