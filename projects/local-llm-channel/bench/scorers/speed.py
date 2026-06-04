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

"""Speed metric aggregates."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SpeedAggregate:
    median_tok_per_sec: float
    max_peak_vram_mb: int


def aggregate_speed_metrics(
    tok_rates: list[float], peaks: list[int]
) -> SpeedAggregate:
    import statistics

    med = statistics.median(tok_rates) if tok_rates else 0.0
    peak = max(peaks) if peaks else 0
    return SpeedAggregate(median_tok_per_sec=med, max_peak_vram_mb=peak)
