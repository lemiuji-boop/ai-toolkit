#!/usr/bin/env python3
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

"""Обновление .cursor/phase-state.json после gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / ".cursor" / "phase-state.json"


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if action == "pass":
        data["last_gate"] = "pass"
        data["current_phase"] = int(data["current_phase"]) + 1
        data["attempts"] = 0
        data["status"] = "idle"
    elif action == "fail":
        data["last_gate"] = "fail"
        data["attempts"] = int(data.get("attempts", 0)) + 1
        data["status"] = "idle"
        if data["attempts"] >= int(data.get("max_attempts_per_phase", 3)):
            data["status"] = "blocked"
    STATE_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
