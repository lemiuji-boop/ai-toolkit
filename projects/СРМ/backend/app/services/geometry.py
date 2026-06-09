"""Геометрия из 3D (эталон размеров) и дерево изделия (FR-010).

Использует cadquery/OpenCASCADE, если установлен (extra 'cad'); иначе — заглушка.
Полное чтение дерева сборки (экземпляры/количества) из NX/CATIA через XCAF —
документированная точка расширения (СЕРВИС-03); здесь cad-ветка возвращает
одиночную деталь, а входимость по дереву считает расчётное ядро (calc.py, FR-014).
"""
import json
import pathlib
import tempfile
from typing import Any

_RULES_PATH = pathlib.Path(__file__).parent.parent / "data" / "rules.json"
_RULES = json.loads(_RULES_PATH.read_text(encoding="utf-8"))
DENSITY = _RULES["density"]


def _mass_for(volume_cm3: float, material: str | None) -> float | None:
    """Масса по объёму и плотности материала; None — если марка неизвестна."""
    if material in DENSITY:
        return round(volume_cm3 * DENSITY[material] / 1000.0, 4)
    return None


def _leaf_node(designation: str | None, material: str | None,
               volume_cm3: float | None, bbox_mm: list[float],
               mass_kg: float | None, qty: int = 1) -> dict:
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


def _stub(material: str | None) -> dict:
    vol = 151.0
    mass = _mass_for(vol, material)
    bbox = [180.0, 90.0, 24.0]
    out: dict[str, Any] = {
        "volume_cm3": vol,
        "bbox_mm": bbox,
        "source": "stub",
        "is_assembly": False,
        "assembly_tree": _leaf_node(None, material, vol, bbox, mass),
    }
    if mass is not None:
        out["mass_kg"] = mass
        out["density_used"] = DENSITY[material]
    return out


def stub_assembly(material: str | None = "Д16") -> dict:
    """Демонстрационная сборка для тестов входимости (FR-014).

    Корень (1 шт) содержит две детали: кронштейн (2 шт) и нервюру (4 шт).
    """
    mass = _mass_for(151.0, material)
    bracket = _leaf_node("АБВГ.001.001", material, 151.0, [180.0, 90.0, 24.0], mass, qty=2)
    bracket["name"] = "Кронштейн"
    rib = _leaf_node("АБВГ.001.002", material, 90.0, [200.0, 120.0, 8.0],
                     _mass_for(90.0, material), qty=4)
    rib["name"] = "Нервюра"
    root = {
        "designation": "АБВГ.000.000",
        "name": "Узел крепления",
        "material": None,
        "qty": 1,
        "volume_cm3": None,
        "bbox_mm": [],
        "mass_kg": None,
        "children": [bracket, rib],
    }
    return {
        "volume_cm3": None,
        "bbox_mm": [],
        "source": "stub",
        "is_assembly": True,
        "assembly_tree": root,
    }


def geometry(step_bytes: bytes, material: str | None = None) -> dict:
    try:
        import cadquery as cq  # type: ignore

        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
            f.write(step_bytes)
            path = f.name
        # .val() возвращает union-тип cadquery; для импортированного STEP это Shape.
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
    except Exception:
        return _stub(material)
