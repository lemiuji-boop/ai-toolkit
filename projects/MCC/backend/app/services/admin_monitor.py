"""Мониторинг локальных сервисов МАТНОРМ (только localhost, без egress)."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path

import httpx

from app.core.config import settings
from app.services.admin_exports import read_tunnel_url

_PROBE_TIMEOUT = 2.0

# Имена сервисов для API админки
SERVICE_NAMES = ("backend", "rag", "ollama", "addin", "tunnel")

# Подсказки запуска для админ-панели
LAUNCH_HINTS: dict[str, str] = {
    "backend": "./scripts/start-matnorm-stack.sh или uvicorn app.main:app --port 8123",
    "rag": "./scripts/start-rag.sh",
    "ollama": "systemctl start ollama или ollama serve",
    "addin": "./scripts/package-addin.sh; статика на :8123/addin/",
    "tunnel": "./scripts/start-tunnel.sh",
}

_RULES_PATH = Path(__file__).resolve().parent.parent / "data" / "rules.json"


def _rules_version() -> str:
    """Версия rules.json — хеш содержимого (без раскрытия правил в логах)."""
    try:
        data = _RULES_PATH.read_bytes()
        import hashlib

        return hashlib.sha256(data).hexdigest()[:12]
    except OSError:
        return "unavailable"


async def _probe_url(url: str, path: str = "/health") -> dict:
    """Проверка HTTP-сервиса с замером задержки."""
    target = f"{url.rstrip('/')}{path}"
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=_PROBE_TIMEOUT) as client:
            resp = await client.get(target)
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        ok = resp.status_code == 200
        detail: dict = {"ok": ok, "latency_ms": latency_ms, "status_code": resp.status_code}
        if ok:
            try:
                detail["body"] = resp.json()
            except json.JSONDecodeError:
                detail["body"] = None
        return detail
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        return {
            "ok": False,
            "latency_ms": latency_ms,
            "error": type(exc).__name__,
            "source": "stub",
        }


async def probe_backend() -> dict:
    return await _probe_url(settings.backend_url)


async def probe_rag() -> dict:
    return await _probe_url(settings.rag_url)


async def probe_ollama() -> dict:
    """Ollama: /api/tags вместо /health."""
    started = time.perf_counter()
    target = f"{settings.inference_url.rstrip('/')}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=_PROBE_TIMEOUT) as client:
            resp = await client.get(target)
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        ok = resp.status_code == 200
        models: list[str] = []
        if ok:
            try:
                models = [m.get("name", "") for m in resp.json().get("models", [])]
            except (json.JSONDecodeError, AttributeError, TypeError):
                models = []
        return {
            "ok": ok,
            "latency_ms": latency_ms,
            "status_code": resp.status_code,
            "models": models[:5],
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        return {
            "ok": False,
            "latency_ms": latency_ms,
            "error": type(exc).__name__,
            "source": "stub",
            "models": [],
        }


async def probe_tunnel() -> dict:
    """Cloudflare tunnel: URL из .tunnel-url и проверка /health через публичный адрес."""
    url = read_tunnel_url()
    if not url:
        return {
            "ok": False,
            "latency_ms": None,
            "error": "no_tunnel_url",
            "source": "stub",
            "launch_hint": LAUNCH_HINTS["tunnel"],
        }
    started = time.perf_counter()
    target = f"{url.rstrip('/')}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(target)
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        ok = resp.status_code == 200
        return {
            "ok": ok,
            "latency_ms": latency_ms,
            "status_code": resp.status_code,
            "url": url,
            "launch_hint": LAUNCH_HINTS["tunnel"],
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        return {
            "ok": False,
            "latency_ms": latency_ms,
            "error": type(exc).__name__,
            "url": url,
            "source": "stub",
            "launch_hint": LAUNCH_HINTS["tunnel"],
        }


async def probe_rag_version() -> dict:
    """Версия RAG и размер корпуса (GET /version)."""
    started = time.perf_counter()
    target = f"{settings.rag_url.rstrip('/')}/version"
    try:
        async with httpx.AsyncClient(timeout=_PROBE_TIMEOUT) as client:
            resp = await client.get(target)
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        if resp.status_code != 200:
            return {"ok": False, "latency_ms": latency_ms, "status_code": resp.status_code}
        body = resp.json()
        return {
            "ok": True,
            "latency_ms": latency_ms,
            "version": body.get("version"),
            "backend": body.get("backend"),
            "embed_backend": body.get("embed_backend"),
            "chunk_count": body.get("chunk_count"),
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        return {"ok": False, "latency_ms": latency_ms, "error": type(exc).__name__}


async def probe_addin() -> dict:
    """Статика надстройки: GET корня или taskpane."""
    started = time.perf_counter()
    base = settings.addin_url.rstrip("/")
    for path in ("/taskpane.html", "/"):
        target = f"{base}{path}"
        try:
            async with httpx.AsyncClient(timeout=_PROBE_TIMEOUT) as client:
                resp = await client.get(target)
            latency_ms = round((time.perf_counter() - started) * 1000, 1)
            if resp.status_code == 200:
                return {"ok": True, "latency_ms": latency_ms, "status_code": 200, "path": path}
        except Exception:
            continue
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    return {
        "ok": False,
        "latency_ms": latency_ms,
        "error": "unreachable",
        "source": "stub",
    }


async def probe_service(name: str) -> dict:
    probes = {
        "backend": probe_backend,
        "rag": probe_rag,
        "ollama": probe_ollama,
        "addin": probe_addin,
    }
    fn = probes.get(name)
    if fn is None:
        return {"ok": False, "error": "unknown_service", "source": "stub"}
    return await fn()


async def probe_all() -> dict[str, dict]:
    backend = await probe_backend()
    rag = await probe_rag()
    ollama = await probe_ollama()
    addin = await probe_addin()
    tunnel = await probe_tunnel()
    for name, info in (
        ("backend", backend),
        ("rag", rag),
        ("ollama", ollama),
        ("addin", addin),
        ("tunnel", tunnel),
    ):
        if "launch_hint" not in info:
            info["launch_hint"] = LAUNCH_HINTS.get(name, "")
    return {
        "backend": backend,
        "rag": rag,
        "ollama": ollama,
        "addin": addin,
        "tunnel": tunnel,
    }


def aggregate_status(services: dict[str, dict]) -> str:
    """ok / degraded / down — по доступности backend и вспомогательных сервисов."""
    if not services.get("backend", {}).get("ok"):
        return "down"
    aux = [services[k]["ok"] for k in ("rag", "ollama", "addin", "tunnel") if k in services]
    if all(aux):
        return "ok"
    return "degraded"


def collect_gpu_metrics() -> dict:
    """Метрики GPU через nvidia-smi; пустой список при отсутствии GPU."""
    if shutil.which("nvidia-smi") is None:
        return {"gpus": [], "source": "stub", "reason": "nvidia-smi not found"}

    cmd = [
        "nvidia-smi",
        "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if proc.returncode != 0:
            return {"gpus": [], "source": "stub", "reason": "nvidia-smi failed"}

        gpus: list[dict] = []
        for line in proc.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 5:
                continue
            name, util, mem_used, mem_total, temp = parts[:5]
            def _f(val: str) -> float | None:
                try:
                    return float(val)
                except ValueError:
                    return None

            gpus.append(
                {
                    "name": name,
                    "utilization_pct": _f(util),
                    "memory_used_mb": _f(mem_used),
                    "memory_total_mb": _f(mem_total),
                    "temperature_c": _f(temp),
                }
            )
        return {"gpus": gpus, "source": "nvidia-smi"}
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return {"gpus": [], "source": "stub", "reason": "probe error"}


def _read_meminfo() -> dict:
    """Память хоста из /proc/meminfo (stdlib, без psutil)."""
    try:
        info: dict[str, int] = {}
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                key, _, val = line.partition(":")
                info[key.strip()] = int(val.strip().split()[0])
        total_kb = info.get("MemTotal", 0)
        avail_kb = info.get("MemAvailable", info.get("MemFree", 0))
        used_kb = max(total_kb - avail_kb, 0)
        return {
            "total_mb": round(total_kb / 1024, 1),
            "used_mb": round(used_kb / 1024, 1),
            "available_mb": round(avail_kb / 1024, 1),
        }
    except OSError:
        return {"total_mb": None, "used_mb": None, "available_mb": None, "source": "stub"}


def _read_loadavg() -> dict:
    """Загрузка CPU из /proc/loadavg."""
    try:
        with open("/proc/loadavg", encoding="utf-8") as f:
            parts = f.read().split()
        return {
            "load_1m": float(parts[0]),
            "load_5m": float(parts[1]),
            "load_15m": float(parts[2]),
        }
    except (OSError, IndexError, ValueError):
        return {"load_1m": None, "load_5m": None, "load_15m": None, "source": "stub"}


def collect_system_metrics() -> dict:
    gpu = collect_gpu_metrics()
    memory = _read_meminfo()
    load = _read_loadavg()
    return {
        "gpu": gpu,
        "memory": memory,
        "cpu_load": load,
    }


def system_info() -> dict:
    return {
        "service": "matnorm-backend",
        "version": "0.1.0",
        "inference_model": settings.vlm_model,
        "inference_url": settings.inference_url,
        "rules_version": _rules_version(),
        "rag_url": settings.rag_url,
        "addin_url": settings.addin_url,
        "tunnel_url": read_tunnel_url(),
    }
