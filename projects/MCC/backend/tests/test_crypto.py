import os
import pytest
os.environ.setdefault("SECRET_KEY", "test-secret")
from app.core import crypto


def test_roundtrip_and_mask():
    token = crypto.encrypt_key("sk-abcdef123456")
    assert token != "sk-abcdef123456"
    assert crypto.decrypt_key(token) == "sk-abcdef123456"
    assert crypto.mask_key("sk-abcdef123456") == "••••3456"


def test_requires_secret(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError):
        crypto.encrypt_key("x")
