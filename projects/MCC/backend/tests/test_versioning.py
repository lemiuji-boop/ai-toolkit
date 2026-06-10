from datetime import datetime
from app.services.versioning import Decision, VersionInfo, resolve

T1 = datetime(2026, 1, 1); T2 = datetime(2026, 2, 1)


def v(h, doc=None, mtime=T1):
    return VersionInfo(file_hash=h, doc_date=doc, mtime=mtime)


def test_first_version_actual():
    assert resolve(v("h1"), None, frozenset()) is Decision.first_actual


def test_hash_duplicate_skipped():
    assert resolve(v("h1"), v("h1"), frozenset({"h1"})) is Decision.skip_duplicate


def test_newer_supersedes_by_doc_date():
    cur = v("h1", doc=T1)
    inc = v("h2", doc=T2)
    assert resolve(inc, cur, frozenset({"h1"})) is Decision.supersede


def test_older_goes_archive_mtime_fallback():
    cur = v("h1", mtime=T2)         # doc_date нет → mtime
    inc = v("h2", mtime=T1)
    assert resolve(inc, cur, frozenset({"h1"})) is Decision.incoming_archive
