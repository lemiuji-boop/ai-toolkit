"""Тестовые заглушки геометрии (только tests/, не в поставке app/)."""

from typing import Any


def _mass_for(volume_cm3: float, material: str | None, density: dict[str, float]) -> float | None:
    if material in density:
        return round(volume_cm3 * density[material] / 1000.0, 4)
    return None


def _leaf_node(
    designation: str | None,
    material: str | None,
    volume_cm3: float | None,
    bbox_mm: list[float],
    mass_kg: float | None,
    qty: int = 1,
) -> dict:
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


def single_part_stub(material: str | None = "Д16") -> dict[str, Any]:
    density = {"Д16": 2.78}
    vol = 151.0
    mass = _mass_for(vol, material, density)
    bbox = [180.0, 90.0, 24.0]
    out: dict[str, Any] = {
        "volume_cm3": vol,
        "bbox_mm": bbox,
        "source": "test-fixture",
        "is_assembly": False,
        "assembly_tree": _leaf_node(None, material, vol, bbox, mass),
    }
    if mass is not None:
        out["mass_kg"] = mass
        out["density_used"] = density[material]
    return out


def stub_assembly(material: str | None = "Д16") -> dict[str, Any]:
    density = {"Д16": 2.78}
    mass = _mass_for(151.0, material, density)
    bracket = _leaf_node("АБВГ.001.001", material, 151.0, [180.0, 90.0, 24.0], mass, qty=2)
    bracket["name"] = "Кронштейн"
    rib = _leaf_node(
        "АБВГ.001.002",
        material,
        90.0,
        [200.0, 120.0, 8.0],
        _mass_for(90.0, material, density),
        qty=4,
    )
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
        "source": "test-fixture",
        "is_assembly": True,
        "assembly_tree": root,
    }
