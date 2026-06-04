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

"""Peak VRAM sampling via NVML (background thread)."""
from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass

from core.config import get_settings


def estimate_weights_gb(params_b: float, quant: str = "Q4_K_M") -> float:
    """Оценка VRAM под веса: params_B × 0.6 для Q4_K_M."""
    factor = 0.6 if "Q4" in quant.upper() else 0.8
    return params_b * factor


def fits_budget(est_weights_gb: float, kv_headroom_ratio: float = 0.15) -> bool:
    """Проверка влезания в бюджет 6 ГБ с запасом под ОС."""
    settings = get_settings()
    usable = settings.gpu_vram_gb - settings.vram_safety_gb
    kv = est_weights_gb * kv_headroom_ratio
    return (est_weights_gb + kv) <= usable


@dataclass
class VramSampleResult:
    peak_mb: int
    samples: int


class PeakVramSampler:
    """Сэмплирует usedGpuMemory каждые 100 мс в фоновом потоке."""

    def __init__(self, interval_s: float = 0.1) -> None:
        self._interval = interval_s
        self._peak_mb = 0
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._samples = 0

    def _sample_loop(self) -> None:
        try:
            import pynvml

            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            while not self._stop.is_set():
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                used_mb = int(info.used / (1024 * 1024))
                self._peak_mb = max(self._peak_mb, used_mb)
                self._samples += 1
                time.sleep(self._interval)
        except Exception:
            # Fallback: парсинг nvidia-smi один раз при остановке
            pass

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def stop(self) -> VramSampleResult:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        if self._peak_mb == 0:
            self._peak_mb = _nvidia_smi_peak_mb()
        return VramSampleResult(peak_mb=self._peak_mb, samples=self._samples)


def _nvidia_smi_peak_mb() -> int:
    import subprocess

    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            text=True,
            timeout=5,
        )
        return int(out.strip().split("\n")[0])
    except Exception:
        return 0


async def sample_peak_vram_async(duration_s: float = 0.5) -> int:
    """Async wrapper: короткий замер peak VRAM."""
    sampler = PeakVramSampler()
    sampler.start()
    await asyncio.sleep(duration_s)
    result = await asyncio.to_thread(sampler.stop)
    return result.peak_mb
