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

"""Доступ к сетевому/локальному каталогу с write-probe."""

from __future__ import annotations

import enum
import hashlib
import shutil
import time
import uuid
from pathlib import Path

from app.core.config import settings


class StorageAccessMode(str, enum.Enum):
    READ_ONLY = "READ_ONLY"
    READ_WRITE = "READ_WRITE"


class StoragePermissionError(PermissionError):
    """Операция запрещена из-за режима READ_ONLY."""


class NetworkStorage:
    def __init__(self, root: str | None = None) -> None:
        self.root = Path(root or settings.catalog_root)
        self._cached_mode: StorageAccessMode | None = None
        self._cached_at: float = 0.0

    def inbox_path(self) -> Path:
        return self.root / settings.inbox_subdir

    def archive_path(self) -> Path:
        return self.root / settings.archive_subdir

    def catalog_path(self) -> Path:
        return self.root / settings.catalog_subdir

    def check_access(self, force_refresh: bool = False) -> StorageAccessMode:
        ttl = settings.storage_probe_cache_minutes * 60
        now = time.time()
        if not force_refresh and self._cached_mode and (now - self._cached_at) < ttl:
            return self._cached_mode

        if not self.root.exists():
            self._cached_mode = StorageAccessMode.READ_ONLY
            self._cached_at = now
            return self._cached_mode

        probe = self.root / f".kdcatalog_probe_{uuid.uuid4().hex}"
        try:
            probe.write_text("probe", encoding="utf-8")
            probe.unlink(missing_ok=True)
            mode = StorageAccessMode.READ_WRITE
        except OSError:
            mode = StorageAccessMode.READ_ONLY

        self._cached_mode = mode
        self._cached_at = now
        return mode

    def _require_write(self) -> None:
        if self.check_access() != StorageAccessMode.READ_WRITE:
            raise StoragePermissionError("Каталог доступен только для чтения")

    def mkdir(self, path: Path) -> Path:
        self._require_write()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def file_hash(path: Path) -> str:
        digest = hashlib.sha256()
        digest.update(path.read_bytes())
        return digest.hexdigest()

    def copy_file(self, src: Path, dst: Path) -> Path:
        self._require_write()
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if self.file_hash(src) != self.file_hash(dst):
            raise IOError("Хэш после копирования не совпадает")
        return dst

    def move_file(self, src: Path, dst: Path) -> Path:
        """Атомарное перемещение: copy → verify hash → delete source."""
        self.copy_file(src, dst)
        src_hash = self.file_hash(src)
        dst_hash = self.file_hash(dst)
        if src_hash != dst_hash:
            raise IOError("Хэш целевого файла не совпадает с исходным")
        self._require_write()
        src.unlink(missing_ok=True)
        return dst

    def delete_file(self, path: Path) -> None:
        self._require_write()
        path.unlink(missing_ok=True)


storage = NetworkStorage()
