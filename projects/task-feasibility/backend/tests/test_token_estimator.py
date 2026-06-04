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

"""Тесты оценки токенов."""

from app.config import Settings
from app.services.token_estimator import estimate_cost_usd, estimate_tokens


def test_l1_low_iterations() -> None:
    settings = Settings()
    tokens = estimate_tokens("L1", 0, settings)
    assert tokens["debug_iterations"] == 1
    costs = estimate_cost_usd(tokens, settings)
    assert costs["development_usd"] >= 0
