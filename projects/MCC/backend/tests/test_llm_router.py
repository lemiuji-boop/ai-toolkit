import pytest
from app.services.llm.base import DataClass, ProviderInfo
from app.services.llm.router import NoLocalProviderError, NoProviderError, choose


class _P:
    def __init__(self, **kw):
        self.info = ProviderInfo(id=kw.get("id", 1), name=kw.get("name", "p"),
                                 kind=kw["kind"], base_url="http://x", model="m",
                                 enabled=kw.get("enabled", True),
                                 priority=kw.get("priority", 100))
    async def chat_text(self, p): return "{}"
    async def chat_vision(self, p, i): return "{}"


def test_confidential_requires_local():
    ext = _P(kind="external")
    with pytest.raises(NoLocalProviderError):
        choose(DataClass.confidential, lambda: [ext])


def test_confidential_picks_local_by_priority():
    a = _P(kind="local", priority=50, name="a")
    b = _P(kind="local", priority=10, name="b")
    ext = _P(kind="external", priority=1)
    assert choose(DataClass.confidential, lambda: [a, ext, b]).info.name == "b"


def test_open_any_enabled_disabled_skipped():
    off = _P(kind="external", enabled=False, priority=1)
    on = _P(kind="external", priority=5, name="on")
    assert choose(DataClass.open, lambda: [off, on]).info.name == "on"
    with pytest.raises(NoProviderError):
        choose(DataClass.open, lambda: [off])
