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

"""Rule-based scorers: exact, regex, json, code-exec."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from core.models import ScorerType


def score_exact(output: str, expected: str | None) -> tuple[float, dict[str, object]]:
    if not expected:
        return 0.0, {"reason": "no expected"}
    ok = expected.strip() in output
    return (1.0 if ok else 0.0), {"match": ok}


def score_regex(output: str, pattern: str) -> tuple[float, dict[str, object]]:
    ok = bool(re.search(pattern, output, re.MULTILINE | re.DOTALL))
    return (1.0 if ok else 0.0), {"pattern": pattern, "match": ok}


def score_json_valid(output: str) -> tuple[float, dict[str, object]]:
    try:
        # Извлечь первый JSON-блок
        start = output.find("{")
        end = output.rfind("}") + 1
        if start < 0 or end <= start:
            return 0.0, {"error": "no json"}
        obj = json.loads(output[start:end])
        return 1.0, {"parsed": obj}
    except json.JSONDecodeError as e:
        return 0.0, {"error": str(e)}


def score_code_exec(output: str, test_code: str) -> tuple[float, dict[str, object]]:
    """Sandbox: subprocess без сети, timeout 5s."""
    with tempfile.TemporaryDirectory() as tmp:
        mod = Path(tmp) / "solution.py"
        # Вытащить код из markdown fence если есть
        code = output
        if "```" in output:
            parts = output.split("```")
            for p in parts:
                if "def " in p:
                    code = p.replace("python", "", 1).strip()
                    break
        mod.write_text(code + "\n\n" + test_code, encoding="utf-8")
        try:
            proc = subprocess.run(
                ["python3", str(mod)],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=tmp,
            )
            ok = proc.returncode == 0
            return (1.0 if ok else 0.0), {"stdout": proc.stdout, "stderr": proc.stderr}
        except subprocess.TimeoutExpired:
            return 0.0, {"error": "timeout"}


def score_run(
    output: str, scorer: ScorerType, expected: str | None, config: dict[str, object]
) -> tuple[float, dict[str, object]]:
    if scorer == ScorerType.exact:
        return score_exact(output, expected)
    if scorer == ScorerType.regex:
        return score_regex(output, str(config.get("pattern", "")))
    if scorer == ScorerType.json_scorer:
        return score_json_valid(output)
    if scorer == ScorerType.code:
        return score_code_exec(output, str(config.get("test", "pass")))
    return 0.0, {"reason": "unsupported scorer"}
