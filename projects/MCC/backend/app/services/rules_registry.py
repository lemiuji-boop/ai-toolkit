"""Версионируемые правила расчёта (TZ-FINAL FR-063): поле version обязательно,
изменение — только через bump() с инкрементом и diff для audit."""
import json
import pathlib
from typing import Any

RULES_PATH = pathlib.Path(__file__).parent.parent / "data" / "rules.json"


class RulesVersionError(RuntimeError):
    pass


def load(path: pathlib.Path = RULES_PATH) -> dict[str, Any]:
    rules = json.loads(path.read_text(encoding="utf-8"))
    v = rules.get("version")
    if not isinstance(v, int) or v < 1:
        raise RulesVersionError("rules.json must contain integer 'version' >= 1")
    return rules


def diff(old: dict, new: dict, prefix: str = "") -> list[str]:
    out: list[str] = []
    keys = set(old) | set(new)
    for k in sorted(keys):
        p = f"{prefix}.{k}" if prefix else k
        if k not in old:
            out.append(f"+ {p}")
        elif k not in new:
            out.append(f"- {p}")
        elif isinstance(old[k], dict) and isinstance(new[k], dict):
            out.extend(diff(old[k], new[k], p))
        elif old[k] != new[k]:
            out.append(f"~ {p}: {old[k]!r} -> {new[k]!r}")
    return out


def bump(new_rules: dict, expected_current_version: int,
         path: pathlib.Path = RULES_PATH) -> tuple[int, list[str]]:
    """Атомарная смена правил: проверка ожидаемой версии (защита от гонок),
    инкремент, запись. Возвращает (новая версия, diff для audit)."""
    current = load(path)
    if current["version"] != expected_current_version:
        raise RulesVersionError(
            f"version mismatch: expected {expected_current_version}, actual {current['version']}"
        )
    changes = diff(current, new_rules)
    new_rules = dict(new_rules)
    new_rules["version"] = expected_current_version + 1
    path.write_text(json.dumps(new_rules, ensure_ascii=False, indent=2), encoding="utf-8")
    return new_rules["version"], changes
