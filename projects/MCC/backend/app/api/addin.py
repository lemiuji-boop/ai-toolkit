"""API надстройки Excel: каталог экспортов и выгрузка расчётов (SEC-002)."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.services import admin_exports

router = APIRouter(prefix="/api/addin", tags=["addin"])


class CatalogItem(BaseModel):
    path: str
    label: str
    size_bytes: int
    download_url: str
    job_hash: str | None = None
    mode: str | None = None
    verify_ok: bool | None = None
    rows_count: int | None = None
    extract_source: str | None = None
    geometry_source: str | None = None


class CatalogGroups(BaseModel):
    reports: list[CatalogItem]
    jobs: list[CatalogItem]
    reference: list[CatalogItem]


class AddinCatalogResponse(BaseModel):
    groups: CatalogGroups
    total: int
    job_count: int


class FetchJobRequest(BaseModel):
    job_hash: str = Field(..., min_length=12, max_length=12, pattern=r"^[a-f0-9]{12}$")


class ExportRequest(BaseModel):
    path: str = Field(..., min_length=1)


@router.get("/catalog", response_model=AddinCatalogResponse)
def addin_catalog() -> AddinCatalogResponse:
    """Санитизированный каталог готовых данных на сервере."""
    data = admin_exports.list_addin_catalog()
    return AddinCatalogResponse(**data)


@router.post("/fetch-job")
def addin_fetch_job(req: FetchJobRequest) -> dict:
    """Результат расчёта по хешу задания (без обозначений изделий)."""
    payload = admin_exports.fetch_job_by_hash(req.job_hash)
    if payload is None:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return payload


@router.post("/export")
def addin_export(req: ExportRequest) -> dict:
    """Проверка пути и URL скачивания (для чата надстройки)."""
    resolved = admin_exports.resolve_export_path(req.path)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Файл не найден или доступ запрещён")
    return {
        "ok": True,
        "path": req.path,
        "filename": Path(req.path).name,
        "size_bytes": resolved.stat().st_size,
        "download_url": f"/api/addin/download?path={req.path}",
    }


@router.get("/download")
def addin_download(path: str = Query(..., min_length=1)) -> FileResponse:
    """Скачивание файла экспорта (только разрешённые пути под data/exports/)."""
    resolved = admin_exports.resolve_export_path(path)
    if resolved is None:
        raise HTTPException(status_code=404, detail="Файл не найден или доступ запрещён")
    media = "application/octet-stream"
    suffix = resolved.suffix.lower()
    if suffix == ".json":
        media = "application/json"
    elif suffix == ".md":
        media = "text/markdown; charset=utf-8"
    elif suffix == ".csv":
        media = "text/csv; charset=utf-8"
    elif suffix == ".xlsx":
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return FileResponse(
        path=resolved,
        media_type=media,
        filename=Path(path).name,
    )
