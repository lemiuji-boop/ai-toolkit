"""Перекрёстная проверка чертёж ↔ 3D. Геометрия из 3D — эталон размеров."""
from app.core.schemas import ExtractResult, GeometryResult, VerifyResult


def _close(a: float | None, b: float | None, tol: float) -> bool | None:
    if a is None or b is None:
        return None
    if b == 0:
        return abs(a) < 1e-6
    return abs(a - b) / abs(b) <= tol


def verify(extract: ExtractResult, geom: GeometryResult, tol: float = 0.05) -> VerifyResult:
    flags: list[str] = []
    d = extract.dimensions_mm
    draw = sorted([v for v in (d.length, d.width, d.height) if v], reverse=True)
    g = geom.bbox_mm
    if len(draw) == 3 and len(g) == 3:
        for i, (dd, gg) in enumerate(zip(draw, g, strict=False)):
            if _close(dd, gg, tol) is False:
                flags.append(f"Габарит {i + 1}: чертёж {dd} мм ≠ 3D {gg} мм (>{int(tol * 100)}%)")
    else:
        flags.append("Габариты с чертежа распознаны не полностью — проверить вручную")
    if extract.mass_kg and geom.mass_kg and _close(extract.mass_kg, geom.mass_kg, 0.10) is False:
        flags.append(f"Масса: чертёж {extract.mass_kg} кг ≠ расчёт {geom.mass_kg} кг (>10%)")
    if not extract.material:
        flags.append("Марка материала не распознана")
    return VerifyResult(ok=len(flags) == 0, flags=flags)
