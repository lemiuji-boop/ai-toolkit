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

import sys
from pathlib import Path

_AI_ROOT = Path(__file__).resolve().parents[1]
if str(_AI_ROOT) not in sys.path:
    sys.path.insert(0, str(_AI_ROOT))

from app.pipeline.stamp_ii import classify_backlog, parse_directives_from_text
from app.pipeline.stamp_kd import DOC_NUMBER_RE


def test_doc_number_regex() -> None:
    assert DOC_NUMBER_RE.search("АБВГ.123456.001")


def test_backlog_classifier() -> None:
    assert classify_backlog("Детали израсходовать") == "use"
    assert classify_backlog("Детали доработать") == "rework"


def test_multiple_directives() -> None:
    text = "АБВГ.123456.001 израсходовать\nАБВГ.123456.002 доработать с изделия № И-200"
    directives = parse_directives_from_text(text)
    assert len(directives) >= 2
