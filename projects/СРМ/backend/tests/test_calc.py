from app.core.schemas import Dimensions, ExtractResult, GeometryResult
from app.services import calc


def test_norm_and_kim():
    ex = ExtractResult(
        material="Д16",
        mass_kg=0.42,
        dimensions_mm=Dimensions(length=180, width=90, height=24),
    )
    geom = GeometryResult(volume_cm3=151.0, bbox_mm=[180, 90, 24], mass_kg=0.42, density_used=2.78)
    rows = calc.build_rows(ex, geom)
    r = rows[0]
    assert r.mz_kg and r.mz_kg > r.md_kg          # заготовка тяжелее детали
    assert r.kim and 0 < r.kim <= 1               # КИМ в долях
    assert r.norm_per_part_kg and r.norm_per_part_kg >= r.mz_kg  # норма с учётом раскроя
