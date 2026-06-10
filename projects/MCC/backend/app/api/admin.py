"""API админ-панели мониторинга МАТНОРМ. Доступ — только с JWT (T-16)."""

import time
from pathlib import Path
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.api.auth import require_admin
from app.core.config import settings
from app.services import admin_exports, admin_monitor, clients_monitor, job_store, providers_store

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])


class AdminStatusResponse(BaseModel):
    status: str
    services: dict[str, dict]
    active_jobs: int = 0
    tunnel_url: str | None = None


class AdminMetricsResponse(BaseModel):
    gpu: dict
    memory: dict
    cpu_load: dict


class AdminJobsResponse(BaseModel):
    jobs: list[dict]
    total: int


class AdminServicesResponse(BaseModel):
    services: dict[str, dict]
    system: dict


class AdminProgressResponse(BaseModel):
    total: int
    completed: int
    failed: int
    in_progress: int
    percent: float
    source: str


class ExportFileItem(BaseModel):
    path: str
    label: str
    size_bytes: int
    category: str
    download_url: str


class AdminExportsResponse(BaseModel):
    files: list[ExportFileItem]
    job_count: int
    addin_zip_url: str | None = None


class AdminRagOverviewResponse(BaseModel):
    health: dict
    version: dict
    description: str


# ---------- Провайдеры ИИ (T-08) ----------


class ProviderItem(BaseModel):
    """Провайдер в ответах API: api_key только маскированный (SEC-002/003)."""

    id: int
    name: str
    kind: Literal["local", "external"]
    base_url: str
    model: str
    api_key_masked: str | None = None
    has_api_key: bool = False
    enabled: bool = True
    priority: int = 100
    created_at: str


class ProvidersListResponse(BaseModel):
    providers: list[ProviderItem]
    presets: dict[str, dict[str, str]]
    allow_external: bool


class ProviderCreateRequest(BaseModel):
    """Создание провайдера; preset подставляет kind/base_url по умолчанию."""

    name: str = Field(min_length=1, max_length=64)
    preset: str | None = None
    kind: Literal["local", "external"] | None = None
    base_url: str | None = Field(default=None, max_length=255)
    model: str = Field(min_length=1, max_length=128)
    api_key: str | None = Field(default=None, max_length=512)
    enabled: bool = True
    priority: int = Field(default=100, ge=0, le=1000)


class ProviderTestResponse(BaseModel):
    ok: bool
    checked: Literal["network", "validation"]
    detail: str
    latency_ms: int | None = None


class ProviderDeleteResponse(BaseModel):
    deleted: bool


@router.get("/providers", response_model=ProvidersListResponse)
def providers_list() -> ProvidersListResponse:
    """Список провайдеров ИИ (ключи маскированы) + пресеты для формы."""
    return ProvidersListResponse(
        providers=[ProviderItem(**rec) for rec in providers_store.list_records()],
        presets=providers_store.PRESETS,
        allow_external=settings.allow_external_providers,
    )


@router.post("/providers", response_model=ProviderItem, status_code=201)
def providers_create(req: ProviderCreateRequest) -> ProviderItem:
    """Создать провайдера: ключ шифруется (SECRET_KEY), в логи/ответы не попадает."""
    preset = providers_store.PRESETS.get(req.preset or "")
    kind = req.kind or (preset["kind"] if preset else None)
    base_url = req.base_url or (preset["base_url"] if preset else None)
    if kind not in ("local", "external"):
        raise HTTPException(status_code=422, detail="Укажите kind=local|external или preset")
    if not base_url:
        raise HTTPException(status_code=422, detail="Укажите base_url или preset")
    if kind == "external" and not req.api_key:
        raise HTTPException(status_code=422, detail="Для внешнего провайдера нужен api_key")
    try:
        rec = providers_store.create_record(
            name=req.name,
            kind=kind,
            base_url=base_url,
            model=req.model,
            api_key=req.api_key,
            enabled=req.enabled,
            priority=req.priority,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return ProviderItem(**rec)


@router.delete("/providers/{provider_id}", response_model=ProviderDeleteResponse)
def providers_delete(provider_id: int) -> ProviderDeleteResponse:
    """Удалить провайдера (вместе с зашифрованным ключом)."""
    if not providers_store.delete_record(provider_id):
        raise HTTPException(status_code=404, detail="Провайдер не найден")
    return ProviderDeleteResponse(deleted=True)


@router.post("/providers/{provider_id}/test", response_model=ProviderTestResponse)
async def providers_test(provider_id: int) -> ProviderTestResponse:
    """Проверка провайдера.

    local — сетевая проба Ollama (/api/tags) в локальном контуре.
    external — БЕЗ выхода в сеть (SEC-001): только валидация конфигурации;
    реальная проба возможна лишь при ALLOW_EXTERNAL_PROVIDERS=1.
    """
    rec = providers_store.get_record(provider_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Провайдер не найден")

    if rec["kind"] == "local":
        t0 = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{rec['base_url'].rstrip('/')}/api/tags")
                r.raise_for_status()
                models = [m.get("name", "") for m in r.json().get("models", [])]
        except httpx.HTTPError as exc:
            return ProviderTestResponse(
                ok=False, checked="network",
                detail=f"Ollama недоступен: {type(exc).__name__}",
            )
        latency = int((time.monotonic() - t0) * 1000)
        if rec["model"] and not any(m.startswith(rec["model"]) for m in models):
            return ProviderTestResponse(
                ok=False, checked="network", latency_ms=latency,
                detail=f"Ollama доступен, но модель '{rec['model']}' не установлена "
                       f"(ollama pull {rec['model']})",
            )
        return ProviderTestResponse(
            ok=True, checked="network", latency_ms=latency,
            detail=f"Ollama доступен, моделей: {len(models)}",
        )

    # Внешний провайдер.
    if not settings.allow_external_providers:
        problems: list[str] = []
        if not rec.get("api_key_encrypted"):
            problems.append("не задан api_key")
        if not rec["base_url"].startswith("https://"):
            problems.append("base_url должен быть https://")
        if problems:
            return ProviderTestResponse(
                ok=False, checked="validation", detail="; ".join(problems),
            )
        return ProviderTestResponse(
            ok=True, checked="validation",
            detail="Конфигурация корректна. Сетевая проба не выполнялась: SEC-001 "
                   "(исходящие вызовы запрещены). Для реальной пробы установите "
                   "ALLOW_EXTERNAL_PROVIDERS=1 после согласования с ИБ.",
        )

    # ALLOW_EXTERNAL_PROVIDERS=1 — явно разрешённая сетевая проба (без передачи КД).
    t0 = time.monotonic()
    provider = providers_store.runtime_provider(rec)
    headers = {"Authorization": f"Bearer {provider.info.api_key}"} if provider.info.api_key else {}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{rec['base_url'].rstrip('/')}/v1/models", headers=headers)
        latency = int((time.monotonic() - t0) * 1000)
        if r.status_code in (200, 404):
            # 404 допустим: не все API дают /v1/models, но соединение и TLS работают.
            return ProviderTestResponse(
                ok=True, checked="network", latency_ms=latency,
                detail=f"Соединение установлено (HTTP {r.status_code})",
            )
        if r.status_code in (401, 403):
            return ProviderTestResponse(
                ok=False, checked="network", latency_ms=latency,
                detail=f"Ключ отклонён (HTTP {r.status_code})",
            )
        return ProviderTestResponse(
            ok=False, checked="network", latency_ms=latency,
            detail=f"Неожиданный ответ: HTTP {r.status_code}",
        )
    except httpx.HTTPError as exc:
        return ProviderTestResponse(
            ok=False, checked="network", detail=f"Сетевая ошибка: {type(exc).__name__}",
        )


# ---------- Подключения клиентов ----------


class ClientItem(BaseModel):
    """Клиент LAN: только IP/UA/endpoint, без содержимого запросов (SEC-002)."""

    ip: str
    first_seen: str
    last_seen: str
    requests: int
    last_endpoint: str | None = None
    user_agent: str | None = None


class AdminClientsResponse(BaseModel):
    clients: list[ClientItem]
    server_ips: list[str]


def _server_ips() -> list[str]:
    """IP-адреса самого сервера — чтобы UI подсветил внешние ПК (Excel)."""
    import socket

    ips = {"127.0.0.1", "::1", "localhost"}
    try:
        host = socket.gethostname()
        for info in socket.getaddrinfo(host, None):
            ips.add(str(info[4][0]))
    except OSError:
        pass
    return sorted(ips)


@router.get("/clients", response_model=AdminClientsResponse)
def admin_clients() -> AdminClientsResponse:
    """Подключения к /api/* и /addin/*: ПК с Excel виден как не-серверный IP."""
    return AdminClientsResponse(
        clients=[ClientItem(**rec) for rec in clients_monitor.list_clients()],
        server_ips=_server_ips(),
    )


@router.get("/status", response_model=AdminStatusResponse)
async def admin_status() -> AdminStatusResponse:
    """Агрегированное состояние backend, RAG, Ollama, add-in, tunnel."""
    services = await admin_monitor.probe_all()
    status = admin_monitor.aggregate_status(services)
    return AdminStatusResponse(
        status=status,
        services=services,
        active_jobs=job_store.active_jobs_count(),
        tunnel_url=admin_exports.read_tunnel_url(),
    )


@router.get("/progress", response_model=AdminProgressResponse)
def admin_progress() -> AdminProgressResponse:
    """Прогресс пакетного экспорта (report_summary или журнал заданий)."""
    data = admin_exports.collect_progress()
    return AdminProgressResponse(**data)


@router.get("/exports", response_model=AdminExportsResponse)
def admin_exports_list() -> AdminExportsResponse:
    """Готовые файлы экспорта (без обозначений изделий в API)."""
    files_raw = admin_exports.list_export_files()
    files = [
        ExportFileItem(
            **item,
            download_url=f"/api/admin/exports/download?path={item['path']}",
        )
        for item in files_raw
    ]
    addin_zip: str | None = None
    if admin_exports.addin_zip_path().is_file():
        addin_zip = "/addin/matnorm-addin.zip"
    return AdminExportsResponse(
        files=files,
        job_count=admin_exports.job_export_count(),
        addin_zip_url=addin_zip,
    )


@router.get("/exports/download")
def admin_exports_download(path: str = Query(..., min_length=1)) -> FileResponse:
    """Скачивание файла экспорта (только разрешённые пути под data/exports/)."""
    resolved = admin_exports.resolve_export_path(path)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Файл не найден или доступ запрещён")
    media = "application/octet-stream"
    if resolved.suffix == ".json":
        media = "application/json"
    elif resolved.suffix == ".md":
        media = "text/markdown; charset=utf-8"
    elif resolved.suffix == ".csv":
        media = "text/csv; charset=utf-8"
    return FileResponse(
        path=resolved,
        media_type=media,
        filename=Path(path).name,
    )


@router.get("/rag/overview", response_model=AdminRagOverviewResponse)
async def admin_rag_overview() -> AdminRagOverviewResponse:
    """Сводка RAG для админ-панели: health, версия, описание."""
    from app.services import rag_client

    health: dict = {"ok": False}
    version: dict = {"ok": False}
    try:
        health = await rag_client.health()
        health["ok"] = health.get("status") == "ok"
    except Exception as exc:
        health = {"ok": False, "error": type(exc).__name__}

    version = await admin_monitor.probe_rag_version()

    description = (
        "RAG индексирует открытые нормативные источники: rules.json, ТЗ (docs/TZ.md), "
        "справочники из data/rag/. Конфиденциальные PDF КД не попадают в индекс "
        "без явного ingest. Поиск: POST /api/rag/search (прокси к :8020)."
    )
    return AdminRagOverviewResponse(health=health, version=version, description=description)


@router.get("/metrics", response_model=AdminMetricsResponse)
def admin_metrics() -> AdminMetricsResponse:
    """GPU (nvidia-smi), память и загрузка CPU (через /proc)."""
    m = admin_monitor.collect_system_metrics()
    return AdminMetricsResponse(gpu=m["gpu"], memory=m["memory"], cpu_load=m["cpu_load"])


@router.get("/jobs", response_model=AdminJobsResponse)
def admin_jobs(limit: int = Query(50, ge=1, le=50)) -> AdminJobsResponse:
    """Последние задания: только job_id и хеш входа, без обозначений (SEC-002)."""
    jobs = job_store.list_jobs(limit=limit)
    return AdminJobsResponse(jobs=jobs, total=len(jobs))


@router.get("/services", response_model=AdminServicesResponse)
async def admin_services() -> AdminServicesResponse:
    """Детальный статус сервисов и системная информация."""
    services = await admin_monitor.probe_all()
    return AdminServicesResponse(services=services, system=admin_monitor.system_info())


@router.post("/services/{name}/restart")
async def restart_service(name: str) -> None:
    """Перезапуск сервисов — вне scope каркаса (будущий оркестратор)."""
    if name not in admin_monitor.SERVICE_NAMES:
        raise HTTPException(status_code=404, detail=f"Неизвестный сервис: {name}")
    raise HTTPException(
        status_code=501,
        detail="Перезапуск сервисов не реализован в каркасе; используйте systemd/docker вручную",
    )
