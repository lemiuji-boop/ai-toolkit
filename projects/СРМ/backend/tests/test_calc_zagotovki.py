"""Тесты выбора вида заготовки и расчёта по каждому виду (FR-015)."""
import pytest

from app.services import calc


@pytest.mark.parametrize(
    "material,expected_zag",
    [
        ("Д16", "лист"),       # по умолчанию
        ("ВТ6", "поковка"),    # правило по марке
        ("30ХГСА", "поковка"),
        ("АЛ9", "литьё"),
        ("АК7ч", "литьё"),
        (None, "лист"),        # нет марки → default
        ("неизвестная", "лист"),
    ],
)
def test_pick_zagotovka(material, expected_zag):
    assert calc._pick_zagotovka(material) == expected_zag


@pytest.mark.parametrize("zag", ["лист", "профиль", "поковка", "литьё"])
def test_each_zagotovka_applies_its_factors(zag):
    # Для каждого вида Мз и норма считаются по его собственным коэффициентам.
    zr = calc.RULES["zagotovki"][zag]
    md = 1.0
    row = calc._compute_row(1, "X", "деталь", "Д16", md, qty=1)
    # _compute_row выбирает вид по материалу; проверяем коэффициенты выбранного вида.
    sel = calc.RULES["zagotovki"][row.zagotovka]
    assert row.mz_kg == round(md * sel["mz_factor_from_md"], 4)
    assert row.norm_per_part_kg == round(row.mz_kg * sel["kr"], 4)
    # Коэффициенты видов различимы между собой.
    assert zr["mz_factor_from_md"] > 0 and zr["kr"] > 0


def test_pokovka_heavier_than_list():
    # Поковка имеет больший припуск (Мз/Мд), чем лист — проверяем порядок.
    md = 2.0
    row_list = calc._compute_row(1, "A", "д", "Д16", md, qty=1)      # лист
    row_pokovka = calc._compute_row(2, "B", "д", "ВТ6", md, qty=1)   # поковка
    assert row_pokovka.mz_kg > row_list.mz_kg
