import uuid

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.core.schemas import (
    DataCompleteness,
    ExtractResult,
    GeometryResult,
    JobMode,
    JobModeRequest,
    JobResult,
    NormControlRequest,
    NormControlResponse,
)
from app.services import calc, excel_format, geometry, ocr, verify, vision

router = APIRouter(prefix="/api")


def _extract_from_geometry(geom: GeometryResult) -> ExtractResult:
    """Минимальные поля с чертежа при режиме model_only (из дерева 3D)."""
    node = geom.assembly_tree
    return ExtractResult(
        designation=node.designation if node else None,
        name=node.name if node else None,
        material=node.material if node else None,
        source="model",
    )


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


@router.post("/jobs", response_model=JobResult)
async def create_job(
    drawing: UploadFile | None = File(None),
    model3d: UploadFile | None = File(None),
    mode: JobModeRequest = Query("auto", description="auto|drawing_only|model_only|paired"),
    debug: bool = False,
) -> JobResult:
    drawing_bytes = await drawing.read() if drawing is not None else b""
    model_bytes = await model3d.read() if model3d is not None else b""
    has_drawing = bool(drawing_bytes)
    has_model = bool(model_bytes)

    resolved = _resolve_mode(mode, has_drawing, has_model)
    completeness = DataCompleteness(has_drawing=has_drawing, has_model3d=has_model)

    extract: ExtractResult
    geom: GeometryResult
    debug_info: dict | None = None

    if resolved == "drawing_only":
        extract = vision.extract(drawing_bytes)
        geom = GeometryResult(**geometry._stub(extract.material))
        if debug:
            debug_info = ocr.preprocess(drawing_bytes)[1]

    elif resolved == "model_only":
        geom = GeometryResult(**geometry.geometry(model_bytes, None))
        extract = _extract_from_geometry(geom)

    else:  # paired
        extract = vision.extract(drawing_bytes)
        geom = GeometryResult(**geometry.geometry(model_bytes, extract.material))
        if debug:
            debug_info = ocr.preprocess(drawing_bytes)[1]

    completeness.vision_stub = has_drawing and extract.source == "stub"
    completeness.geometry_stub = geom.source == "stub"

    v = verify.verify(extract, geom, mode=resolved)
    rows = calc.build_rows(extract, geom)

    return JobResult(
        job_id=str(uuid.uuid4()),
        mode=resolved,
        data_completeness=completeness,
        extract=extract,
        geometry=geom,
        verify=v,
        rows=rows,
        debug=debug_info,
    )


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
