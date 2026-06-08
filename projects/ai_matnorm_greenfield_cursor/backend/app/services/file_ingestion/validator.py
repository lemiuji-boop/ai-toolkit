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

import mimetypes
import zipfile
from io import BytesIO
from pathlib import PurePosixPath

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".webp",
    ".zip",
}

ALLOWED_MIMES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/webp",
    "application/zip",
    "application/octet-stream",
}


FORBIDDEN_EXTENSIONS = {".7z", ".rar", ".tar", ".gz", ".bz2"}


def validate_upload(filename: str, content_type: str, size_bytes: int, max_mb: int) -> None:
    ext = PurePosixPath(filename).suffix.lower()
    if ext in FORBIDDEN_EXTENSIONS:
        raise ValueError(f"Архивный формат не поддерживается: {ext}. Используйте ZIP.")
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Расширение не разрешено: {ext}")
    if size_bytes > max_mb * 1024 * 1024:
        raise ValueError(f"Файл превышает лимит {max_mb} МБ")
    guessed, _ = mimetypes.guess_type(filename)
    if content_type not in ALLOWED_MIMES and (guessed not in ALLOWED_MIMES):
        raise ValueError(f"MIME не разрешён: {content_type}")


def safe_extract_zip(data: bytes, max_files: int = 50) -> list[tuple[str, bytes]]:
    """Безопасная распаковка ZIP без zip-slip."""
    results: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(BytesIO(data)) as zf:
        if len(zf.namelist()) > max_files:
            raise ValueError("Слишком много файлов в архиве")
        for name in zf.namelist():
            if name.endswith("/") or ".." in name or name.startswith("/"):
                continue
            ext = PurePosixPath(name).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS or ext == ".zip":
                continue
            results.append((PurePosixPath(name).name, zf.read(name)))
    return results
