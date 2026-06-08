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

"""Ограничение чтения PDF только из CATALOG_ROOT / FILE_STORAGE_ROOT."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import HTTPException, status


def allowed_roots() -> list[Path]:
    roots: list[Path] = []
    for key in ("CATALOG_ROOT", "FILE_STORAGE_ROOT"):
        raw = os.environ.get(key, "")
        if raw:
            roots.append(Path(raw).resolve())
    if not roots:
        roots.append(Path("/data/catalog").resolve())
        roots.append(Path("/data/storage").resolve())
    return roots


def resolve_allowed_path(file_path: str) -> Path:
    try:
        resolved = Path(file_path).resolve()
    except (OSError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path") from exc

    if not resolved.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if resolved.suffix.lower() != ".pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF allowed")

    for root in allowed_roots():
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Path outside allowed storage")
