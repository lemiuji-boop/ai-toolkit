"""Мониторинг подключений клиентов (ПК с Excel и др.) к /api/* и /addin/*.

Кольцевой буфер в памяти + снапшот data/admin/clients.jsonl (одна строка — один
клиент). Хранится только IP, user-agent и последний endpoint — без содержимого
запросов и обозначений изделий (SEC-002).
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

# Максимум различных клиентов в буфере (LAN-пилот — десятки адресов достаточно).
_MAX_CLIENTS = 200

_lock = Lock()
_clients: dict[str, dict] = {}
_loaded = False
_dirty_writes = 0
# Снапшот пишется не чаще, чем раз в N изменений (файл маленький, но не на каждый hit).
_FLUSH_EVERY = 5


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _store_path() -> Path:
    override = os.environ.get("MATNORM_CLIENTS_PATH")
    if override:
        return Path(override)
    return _project_root() / "data" / "admin" / "clients.jsonl"


def _flush_locked() -> None:
    """Записать снапшот на диск (вызывается под _lock)."""
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for rec in _clients.values():
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    tmp.replace(path)


def load_persisted() -> int:
    """Загрузить снапшот клиентов с диска (на старте приложения)."""
    global _loaded
    with _lock:
        if _loaded:
            return len(_clients)
        _loaded = True
        path = _store_path()
        if not path.is_file():
            return 0
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            ip = rec.get("ip")
            if ip:
                _clients[ip] = rec
        return len(_clients)


def record_request(ip: str, path: str, user_agent: str | None) -> None:
    """Зафиксировать обращение клиента (вызывается из middleware)."""
    global _dirty_writes
    now = datetime.now(UTC).isoformat()
    with _lock:
        rec = _clients.get(ip)
        if rec is None:
            if len(_clients) >= _MAX_CLIENTS:
                # Вытеснить самого давнего клиента (кольцевой буфер).
                oldest = min(_clients.values(), key=lambda r: r.get("last_seen", ""))
                _clients.pop(oldest["ip"], None)
            rec = {"ip": ip, "first_seen": now, "requests": 0}
            _clients[ip] = rec
        rec["requests"] = int(rec.get("requests", 0)) + 1
        rec["last_seen"] = now
        rec["last_endpoint"] = path
        if user_agent:
            rec["user_agent"] = user_agent[:200]
        _dirty_writes += 1
        if _dirty_writes >= _FLUSH_EVERY:
            _dirty_writes = 0
            _flush_locked()


def list_clients() -> list[dict]:
    """Клиенты, отсортированные по последнему обращению (новые первыми)."""
    with _lock:
        return sorted(_clients.values(), key=lambda r: r.get("last_seen", ""), reverse=True)


def flush() -> None:
    """Принудительная запись снапшота (останов приложения)."""
    with _lock:
        _flush_locked()


def reset_for_tests() -> None:
    """Сброс состояния (только для unit-тестов)."""
    global _loaded, _dirty_writes
    with _lock:
        _clients.clear()
        _loaded = False
        _dirty_writes = 0
