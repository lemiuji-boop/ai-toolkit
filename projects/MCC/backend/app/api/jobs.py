import uuid

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from app.core.schemas import (
    GeometryResult,
    JobResult,
    NormControlRequest,
    NormControlResponse,
)
from app.services import calc, excel_format, geometry, ocr, verify, vision

router = APIRouter(prefix="/api")


@router.post("/jobs", response_model=JobResult)
async def create_job(
    drawing: UploadFile = File(...),
    model3d: UploadFile | None = File(None),
    debug: bool = False,
) -> JobResult:
    img = await drawing.read()
    extract = vision.extract(img)

    if model3d is not None:
        geom_raw = geometry.geometry(await model3d.read(), extract.material)
    else:
        geom_raw = geometry._stub(extract.material)
    geom = GeometryResult(**geom_raw)

    v = verify.verify(extract, geom)
    rows = calc.build_rows(extract, geom)
    # FR-002: в debug-режиме возвращаем координаты зон OCR-препроцессора.
    debug_info = ocr.preprocess(img)[1] if debug else None
    return JobResult(
        job_id=str(uuid.uuid4()),
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
