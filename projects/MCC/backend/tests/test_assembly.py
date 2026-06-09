"""Тесты дерева изделия и входимости (FR-010/014) — на JSON-заглушке сборки."""
from app.core.schemas import ExtractResult, GeometryResult
from app.services import calc, geometry


def test_stub_assembly_structure():
    # Заглушка-сборка: корень (1 шт) с двумя деталями.
    geom = GeometryResult(**geometry.stub_assembly("Д16"))
    assert geom.is_assembly is True
    assert geom.assembly_tree is not None
    assert len(geom.assembly_tree.children) == 2


def test_vhodimost_per_set():
    # Кронштейн 2 шт + нервюра 4 шт на одну сборку; сборок на с/к — по умолчанию 1.
    geom = GeometryResult(**geometry.stub_assembly("Д16"))
    rows = calc.build_rows(ExtractResult(), geom)
    by_desig = {r.designation: r for r in rows}
    assert by_desig["АБВГ.001.001"].qty_per_set == 2
    assert by_desig["АБВГ.001.002"].qty_per_set == 4
    # Норма на программу = норма на деталь × входимость.
    bracket = by_desig["АБВГ.001.001"]
    assert bracket.norm_per_part_kg is not None
    assert bracket.norm_program_kg == round(bracket.norm_per_part_kg * 2, 4)


def test_vhodimost_scales_with_sets(monkeypatch):
    # Входимость умножается на число сборок на самолёто-комплект.
    monkeypatch.setattr(calc.settings, "sets_per_aircraft", 3)
    geom = GeometryResult(**geometry.stub_assembly("Д16"))
    rows = calc.build_rows(ExtractResult(), geom)
    rib = next(r for r in rows if r.designation == "АБВГ.001.002")
    assert rib.norm_per_part_kg is not None
    assert rib.norm_program_kg == round(rib.norm_per_part_kg * 4 * 3, 4)


def test_single_part_still_one_row():
    # Одиночная деталь по-прежнему даёт одну строку (обратная совместимость).
    geom = GeometryResult(**geometry._stub("Д16"))
    rows = calc.build_rows(
        ExtractResult(designation="АБВГ.001.001", material="Д16"), geom
    )
    assert len(rows) == 1
    assert rows[0].qty_per_set == 1
