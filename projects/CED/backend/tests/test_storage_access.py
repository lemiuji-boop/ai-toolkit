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

import os
import stat
from pathlib import Path

import pytest

from app.services.storage_access import NetworkStorage, StorageAccessMode, StoragePermissionError


def test_write_probe_read_write(tmp_path: Path) -> None:
    store = NetworkStorage(str(tmp_path))
    assert store.check_access(force_refresh=True) == StorageAccessMode.READ_WRITE


def test_move_file_atomic(tmp_path: Path) -> None:
    store = NetworkStorage(str(tmp_path))
    src = tmp_path / "a.pdf"
    dst = tmp_path / "b" / "a.pdf"
    src.write_bytes(b"pdf")
    store.move_file(src, dst)
    assert dst.exists()
    assert not src.exists()


def test_read_only_blocks_write(tmp_path: Path) -> None:
    store = NetworkStorage(str(tmp_path))
    os.chmod(tmp_path, stat.S_IRUSR | stat.S_IXUSR)
    mode = store.check_access(force_refresh=True)
    if mode == StorageAccessMode.READ_ONLY:
        with pytest.raises(StoragePermissionError):
            store.mkdir(tmp_path / "blocked")
    os.chmod(tmp_path, stat.S_IRWXU)
