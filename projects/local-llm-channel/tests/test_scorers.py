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

"""Scorer unit tests."""
from __future__ import annotations

from bench.scorers.rule_based import score_exact, score_json_valid, score_run
from core.models import ScorerType


def test_exact_match() -> None:
    v, _ = score_exact("hello world", "world")
    assert v == 1.0


def test_json_valid() -> None:
    v, _ = score_json_valid('{"a": 1}')
    assert v == 1.0


def test_code_scorer_stub() -> None:
    out = "def reverse_string(s):\n    return s[::-1]"
    v, _ = score_run(out, ScorerType.code, None, {"test": "assert reverse_string('ab')=='ba'"})
    assert v == 1.0
