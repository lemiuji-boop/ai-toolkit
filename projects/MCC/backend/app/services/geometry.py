"""Геометрия из 3D (эталон размеров) и дерево изделия (FR-010).

Использует cadquery/OpenCASCADE (extra 'cad'). Без cadquery — явная ошибка
GEOMETRY_UNAVAILABLE (TZ-FINAL §3), не подмена данными.
"""
import tempfile
from typing import Any

from app.services.errors import GeometryUnavailableError
from app.services.rules_registry import load

DENSITY = load()["density"]


def _mass_for(volume_cm3: float, material: str | None) -> float | None:
    """Масса по объёму и плотности материала; None — если марка неизвестна."""
    if material in DENSITY:
        return round(volume_cm3 * DENSITY[material] / 1000.0, 4)
    return None


def _leaf_node(
    designation: str | None,
    material: str | None,
    volume_cm3: float | None,
    bbox_mm: list[float],
    mass_kg: float | None,
    qty: int = 1,
) -> dict:
    """Лист дерева (деталь)."""
    return {
        "designation": designation,
        "name": None,
        "material": material,
        "qty": qty,
        "volume_cm3": volume_cm3,
        "bbox_mm": bbox_mm,
        "mass_kg": mass_kg,
        "children": [],
    }


def empty_geometry() -> dict[str, Any]:
    """Пустая геометрия, когда 3D не передан (режим drawing_only)."""
    return {
        "volume_cm3": None,
        "bbox_mm": [],
        "source": "none",
        "is_assembly": False,
        "assembly_tree": None,
    }


def geometry(step_bytes: bytes, material: str | None = None) -> dict:
    try:
        import cadquery as cq  # type: ignore

        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
            f.write(step_bytes)
            path = f.name
        shape: Any = cq.importers.importStep(path).val()
        vol_cm3 = round(shape.Volume() / 1000.0, 3)
        bb = shape.BoundingBox()
        dims = [round(d, 2) for d in sorted([bb.xlen, bb.ylen, bb.zlen], reverse=True)]
        mass = _mass_for(vol_cm3, material)
        out: dict[str, Any] = {
            "volume_cm3": vol_cm3,
            "bbox_mm": dims,
            "source": "cad",
            "is_assembly": False,
            "assembly_tree": _leaf_node(None, material, vol_cm3, dims, mass),
        }
        if mass is not None:
            out["mass_kg"] = mass
            out["density_used"] = DENSITY[material]
        return out
    except Exception as exc:
        raise GeometryUnavailableError(
            f"cadquery недоступен или STEP не прочитан: {exc}",
        ) from exc
