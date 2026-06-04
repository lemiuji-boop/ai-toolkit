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

"""Matplotlib charts — dark theme, 1280x720 PNG."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from core.config import get_settings

CHART_SIZE = (12.8, 7.2)
DPI = 100


def _apply_theme() -> None:
    settings = get_settings()
    if settings.chart_theme == "dark":
        plt.style.use("dark_background")


def bar_chart(
    labels: list[str],
    values: list[float],
    title: str,
    ylabel: str,
    out_path: Path,
) -> Path:
    """Bar chart for tok/s or VRAM comparison."""
    _apply_theme()
    fig, ax = plt.subplots(figsize=CHART_SIZE, dpi=DPI)
    ax.bar(labels, values, color="#4a9eff")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=25, ha="right")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="png")
    plt.close(fig)
    return out_path


def line_chart(
    x: list[str],
    y: list[float],
    title: str,
    ylabel: str,
    out_path: Path,
) -> Path:
    _apply_theme()
    fig, ax = plt.subplots(figsize=CHART_SIZE, dpi=DPI)
    ax.plot(x, y, marker="o", color="#4a9eff")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, format="png")
    plt.close(fig)
    return out_path
