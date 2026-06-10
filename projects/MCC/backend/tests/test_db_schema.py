from sqlalchemy import create_engine, inspect
from app.db.models import Base

EXPECTED = {
    "users", "sessions", "providers", "product_sets", "parts", "geometry",
    "notices", "part_versions", "watched_dirs", "scan_runs", "jobs",
    "norm_rows", "corrections", "model_usage", "audit",
}


def test_schema_creates_all_contract_tables():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    assert EXPECTED.issubset(set(inspect(eng).get_table_names()))


def test_part_version_unique_constraint_present():
    cols = {c.name for c in Base.metadata.tables["part_versions"].columns}
    assert {"part_id", "product_set_id", "file_hash", "status", "doc_date"}.issubset(cols)
