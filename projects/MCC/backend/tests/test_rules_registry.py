import json
import pytest
from app.services import rules_registry as rr


def test_load_requires_version(tmp_path):
    p = tmp_path / "rules.json"
    p.write_text(json.dumps({"kim_min": 0.25}), encoding="utf-8")
    with pytest.raises(rr.RulesVersionError):
        rr.load(p)


def test_bump_increments_and_diffs(tmp_path):
    p = tmp_path / "rules.json"
    p.write_text(json.dumps({"version": 1, "kim_min": 0.25}), encoding="utf-8")
    new = {"version": 1, "kim_min": 0.30, "kim_max": 0.92}
    ver, changes = rr.bump(new, expected_current_version=1, path=p)
    assert ver == 2
    assert any("kim_min" in c for c in changes) and any("+ kim_max" in c for c in changes)
    assert rr.load(p)["version"] == 2


def test_bump_version_mismatch(tmp_path):
    p = tmp_path / "rules.json"
    p.write_text(json.dumps({"version": 3}), encoding="utf-8")
    with pytest.raises(rr.RulesVersionError):
        rr.bump({"version": 3}, expected_current_version=2, path=p)


def test_project_rules_have_version():
    assert rr.load()["version"] >= 1
