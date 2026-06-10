import asyncio
import re
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.schemas import (
    DataCompleteness,
    ExtractResult,
    GeometryResult,
    JobMode,
    JobModeRequest,
    JobResult,
    JobStatusResponse,
    JobSubmitResponse,
    NormControlRequest,
    NormControlResponse,
)
from app.services import calc, excel_format, geometry, job_store, ocr, verify, vision
from app.services.errors import GeometryUnavailableError, ServiceError, VisionUnavailableError
from app.services.jobs_runner import InMemoryJobStore, JobRunner
from app.services.rules_registry import load

router = APIRouter(prefix="/api")

_store = InMemoryJobStore()
_runner = JobRunner(_store)

# Буфер входных файлов до завершения задания (для админ-журнала без обозначений).
_pending_inputs: dict[str, tuple[bytes, bytes]] = {}


def _resolve_mode(
    requested: JobModeRequest,
    has_drawing: bool,
    has_model: bool,
) -> JobMode:
    """Определение фактического режима по запросу и наличию файлов."""
    if not has_drawing and not has_model:
        raise HTTPException(
            status_code=422,
            detail="Нужен хотя бы один файл: drawing и/или model3d",
        )

    if requested == "auto":
        if has_drawing and has_model:
            return "paired"
        if has_drawing:
            return "drawing_only"
        return "model_only"

    if requested == "paired":
        if not (has_drawing and has_model):
            raise HTTPException(
                status_code=422,
                detail="Режим paired требует оба файла: drawing и model3d",
            )
        return "paired"

    if requested == "drawing_only":
        if not has_drawing:
            raise HTTPException(
                status_code=422,
                detail="Режим drawing_only требует файл drawing",
            )
        return "drawing_only"

    if not has_model:
        raise HTTPException(
            status_code=422,
            detail="Режим model_only требует файл model3d",
        )
    return "model_only"


async def _run_pipeline(
    stage,
    *,
    drawing_bytes: bytes,
    model_bytes: bytes,
    resolved: JobMode,
    debug: bool,
    job_id: str,
) -> dict[str, Any]:
    """Конвейер задания: распознавание → геометрия → сверка → расчёт."""
    rules_version = load()["version"]
    completeness = DataCompleteness(
        has_drawing=bool(drawing_bytes),
        has_model3d=bool(model_bytes),
    )
    debug_info: dict | None = None

    extract: ExtractResult
    geom: GeometryResult

    if resolved == "drawing_only":
        await stage("распознавание")
        extract = await vision.extract(drawing_bytes)
        extract.rules_version = rules_version
        completeness.vision_available = extract.source == "llm"
        geom = GeometryResult(**geometry.empty_geometry())
        if debug:
            debug_info = ocr.preprocess(drawing_bytes)[1]

    elif resolved == "model_only":
        await stage("геометрия")
        geom_raw = geometry.geometry(model_bytes, None)
        geom = GeometryResult(**geom_raw)
        completeness.geometry_available = geom.source == "cad"
        extract = vision.empty_extract()
        extract.rules_version = rules_version

    else:  # paired
        await stage("распознавание")
        extract = await vision.extract(drawing_bytes)
        extract.rules_version = rules_version
        completeness.vision_available = extract.source == "llm"
        await stage("геометрия")
        geom_raw = geometry.geometry(model_bytes, extract.material)
        geom = GeometryResult(**geom_raw)
        completeness.geometry_available = geom.source == "cad"
        if debug:
            debug_info = ocr.preprocess(drawing_bytes)[1]

    await stage("сверка")
    v = verify.verify(extract, geom, mode=resolved)
    await stage("расчёт")
    rows = calc.build_rows(extract, geom)

    result = JobResult(
        job_id=job_id,
        mode=resolved,
        data_completeness=completeness,
        extract=extract,
        geometry=geom,
        verify=v,
        rows=rows,
        debug=debug_info,
    )
    job_store.register_job(
        result,
        drawing_bytes=drawing_bytes,
        model_bytes=model_bytes,
    )
    return result.model_dump()


def _service_error_payload(exc: ServiceError) -> str:
    return f"[{exc.code}] {exc}"


@router.post("/jobs", status_code=202, response_model=JobSubmitResponse)
async def create_job(
    drawing: UploadFile | None = File(None),
    model3d: UploadFile | None = File(None),
    mode: JobModeRequest = Query("auto", description="auto|drawing_only|model_only|paired"),
    debug: bool = False,
) -> JobSubmitResponse:
    drawing_bytes = await drawing.read() if drawing is not None else b""
    model_bytes = await model3d.read() if model3d is not None else b""
    resolved = _resolve_mode(mode, bool(drawing_bytes), bool(model_bytes))

    ready = asyncio.Event()
    holder: list[str] = [""]

    async def work(stage) -> dict[str, Any]:
        await ready.wait()
        try:
            return await _run_pipeline(
                stage,
                drawing_bytes=drawing_bytes,
                model_bytes=model_bytes,
                resolved=resolved,
                debug=debug,
                job_id=holder[0],
            )
        except (VisionUnavailableError, GeometryUnavailableError) as exc:
            raise RuntimeError(_service_error_payload(exc)) from exc

    job_id = await _runner.submit(work)
    holder[0] = job_id
    ready.set()
    _pending_inputs[job_id] = (drawing_bytes, model_bytes)
    return JobSubmitResponse(job_id=job_id)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: str) -> JobStatusResponse:
    try:
        raw = await _store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc

    error_code: str | None = None
    if raw.get("error"):
        match = re.search(r"\[([A-Z][A-Z0-9_]+)\]", raw["error"])
        if match:
            error_code = match.group(1)

    result = None
    if raw.get("result"):
        result = JobResult(**raw["result"])

    return JobStatusResponse(
        job_id=job_id,
        status=raw["status"],
        stage=raw.get("stage"),
        result=result,
        error=raw.get("error"),
        error_code=error_code,
    )


@router.get("/jobs/{job_id}/events")
async def job_events(job_id: str) -> StreamingResponse:
    try:
        await _store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc

    async def event_stream():
        while True:
            status = (await _store.get(job_id))["status"]
            if status in ("done", "error"):
                stage = (await _store.get(job_id)).get("stage") or status
                yield f"data: {stage}\n\n"
                break
            try:
                evt = await _store.next_event(job_id, timeout=5.0)
                yield f"data: {evt}\n\n"
            except TimeoutError:
                yield ": keepalive\n\n"
            await asyncio.sleep(0.05)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/normcontrol", response_model=NormControlResponse)
def normcontrol(req: NormControlRequest) -> NormControlResponse:
    flags, rows = calc.normcontrol(req.rows)
    return NormControlResponse(flags=flags, rows=rows)


@router.post("/excel/export")
def excel_export(req: NormControlRequest) -> StreamingResponse:
    data = excel_format.to_xlsx(req.rows)
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=vedomost.xlsx"},
    )
