"""Тесты дерева изделия и входимости (FR-010/014) — на тестовых фикстурах сборки."""
from geometry_fixtures import single_part_stub, stub_assembly

from app.core.schemas import ExtractResult, GeometryResult
from app.services import calc


def test_stub_assembly_structure():
    geom = GeometryResult(**stub_assembly("Д16"))
    assert geom.is_assembly is True
    assert geom.assembly_tree is not None
    assert len(geom.assembly_tree.children) == 2


def test_vhodimost_per_set():
    geom = GeometryResult(**stub_assembly("Д16"))
    rows = calc.build_rows(ExtractResult(), geom)
    by_desig = {r.designation: r for r in rows}
    assert by_desig["АБВГ.001.001"].qty_per_set == 2
    assert by_desig["АБВГ.001.002"].qty_per_set == 4
    bracket = by_desig["АБВГ.001.001"]
    assert bracket.norm_per_part_kg is not None
    assert bracket.norm_program_kg == round(bracket.norm_per_part_kg * 2, 4)


def test_vhodimost_scales_with_sets(monkeypatch):
    monkeypatch.setattr(calc.settings, "sets_per_aircraft", 3)
    geom = GeometryResult(**stub_assembly("Д16"))
    rows = calc.build_rows(ExtractResult(), geom)
    rib = next(r for r in rows if r.designation == "АБВГ.001.002")
    assert rib.norm_per_part_kg is not None
    assert rib.norm_program_kg == round(rib.norm_per_part_kg * 4 * 3, 4)


def test_single_part_still_one_row():
    geom = GeometryResult(**single_part_stub("Д16"))
    rows = calc.build_rows(
        ExtractResult(designation="АБВГ.001.001", material="Д16"), geom
    )
    assert len(rows) == 1
    assert rows[0].qty_per_set == 1
