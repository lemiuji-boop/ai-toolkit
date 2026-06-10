"""Детерминированный расчёт норм (по редактируемым правилам rules.json).
Намеренно упрощён для каркаса; формулы и коэффициенты меняются нативно в rules.json.
LLM здесь не участвует."""
from app.core.config import settings
from app.core.schemas import AssemblyNode, ExtractResult, GeometryResult, NormRow
from app.services.rules_registry import load

RULES = load()


def _pick_zagotovka(material: str | None) -> str:
    """Выбор вида заготовки по правилам rules.json (переопределяемо без кода, FR-015).

    Приоритет: явное правило по марке материала → вид по умолчанию.
    Неизвестный вид из правил откатывается к default_zagotovka.
    """
    by_material = RULES.get("zagotovka_by_material", {})
    zag = by_material.get(material or "", RULES["default_zagotovka"])
    if zag not in RULES["zagotovki"]:
        return RULES["default_zagotovka"]
    return zag


def _compute_row(
    num: int,
    designation: str | None,
    name: str | None,
    material: str | None,
    md: float | None,
    qty: int,
) -> NormRow:
    """Расчёт одной строки ведомости по массе детали Мд и входимости qty (FR-011/014)."""
    zag = _pick_zagotovka(material)
    zr = RULES["zagotovki"].get(zag, {})
    kr = zr.get("kr", RULES["default_kr"])

    mz = round(md * zr.get("mz_factor_from_md", 1.35), 4) if md else None
    kim = round(md / mz, 3) if (md and mz) else None
    norm_part = round(mz * kr, 4) if mz else None
    norm_prog = round(norm_part * qty * settings.sets_per_aircraft, 4) if norm_part else None

    flags: list[str] = []
    if kim is not None and kim < RULES["kim_min"]:
        flags.append(f"КИМ {kim} < {RULES['kim_min']}: высокий отход, проверить заготовку")
    if kim is not None and kim > RULES["kim_max"]:
        flags.append(f"КИМ {kim} > {RULES['kim_max']}: проверить Мз/Мд")
    if not material:
        flags.append("Нет марки материала")

    return NormRow(
        num=num,
        designation=designation,
        name=name,
        material=material,
        zagotovka=zag,
        qty_per_set=qty,
        md_kg=md,
        mz_kg=mz,
        kim=kim,
        norm_per_part_kg=norm_part,
        norm_program_kg=norm_prog,
        flags=flags,
    )


def _collect_parts(node: AssemblyNode, mult: int = 1) -> dict:
    """Свёртка дерева изделия в уникальные детали (FR-014).

    Возвращает словарь {(обозначение, материал): {qty, node}}, где qty — суммарная
    входимость детали на одну корневую сборку = произведение кратностей по пути.
    """
    cur = mult * node.qty
    acc: dict = {}
    if not node.children:  # лист — деталь
        acc[(node.designation, node.material)] = {"qty": cur, "node": node}
        return acc
    for child in node.children:
        for key, val in _collect_parts(child, cur).items():
            if key in acc:
                acc[key]["qty"] += val["qty"]
            else:
                acc[key] = val
    return acc


def build_rows(extract: ExtractResult, geom: GeometryResult) -> list[NormRow]:
    # Сборка: строим строку на каждую уникальную деталь с её входимостью (FR-010/014).
    if geom.is_assembly and geom.assembly_tree is not None:
        parts = _collect_parts(geom.assembly_tree)
        rows: list[NormRow] = []
        for i, ((designation, material), info) in enumerate(parts.items(), start=1):
            node: AssemblyNode = info["node"]
            rows.append(
                _compute_row(i, designation, node.name, material, node.mass_kg, info["qty"])
            )
        return rows

    # Одиночная деталь: масса из 3D (эталон) либо с чертежа.
    md = geom.mass_kg or extract.mass_kg
    return [_compute_row(1, extract.designation, extract.name, extract.material, md, qty=1)]


def normcontrol(rows: list[NormRow]) -> tuple[list[str], list[NormRow]]:
    """Повторный нормоконтроль строк (вызывается надстройкой Excel)."""
    all_flags: list[str] = []
    for r in rows:
        r.flags = []
        if r.kim is not None and r.kim < RULES["kim_min"]:
            r.flags.append(f"КИМ < {RULES['kim_min']}")
        if r.kim is not None and r.kim > RULES["kim_max"]:
            r.flags.append(f"КИМ > {RULES['kim_max']}")
        if not r.material:
            r.flags.append("Нет марки материала")
        if r.norm_per_part_kg is None:
            r.flags.append("Не рассчитана норма")
        all_flags.extend(f"Строка {r.num}: {f}" for f in r.flags)
    return all_flags, rows
