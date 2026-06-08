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

import pytest

from app.services.file_ingestion.validator import validate_upload


def test_reject_7z():
    with pytest.raises(ValueError, match="не поддерживается"):
        validate_upload("archive.7z", "application/octet-stream", 1000, 50)


def test_reject_rar():
    with pytest.raises(ValueError, match="не поддерживается"):
        validate_upload("data.rar", "application/octet-stream", 1000, 50)
