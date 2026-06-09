from typing import Literal

from pydantic import BaseModel, Field

# Режимы обработки задания (гибкая загрузка данных).
JobMode = Literal["drawing_only", "model_only", "paired"]
JobModeRequest = Literal["auto", "drawing_only", "model_only", "paired"]


class Dimensions(BaseModel):
    length: float | None = None
    width: float | None = None
    height: float | None = None


class ExtractResult(BaseModel):
    designation: str | None = None
    name: str | None = None
    material: str | None = None
    mass_kg: float | None = None
    dimensions_mm: Dimensions = Dimensions()
    confidence: dict[str, float] = Field(default_factory=dict)
    source: str = "stub"  # "llm" | "stub"


class AssemblyNode(BaseModel):
    """Узел дерева изделия (FR-010). Лист без children — деталь, иначе — сборка."""

    designation: str | None = None
    name: str | None = None
    material: str | None = None
    qty: int = 1  # кратность вхождения узла в родителя
    volume_cm3: float | None = None
    bbox_mm: list[float] = Field(default_factory=list)
    mass_kg: float | None = None
    children: list["AssemblyNode"] = Field(default_factory=list)


class GeometryResult(BaseModel):
    volume_cm3: float | None = None
    bbox_mm: list[float] = Field(default_factory=list)
    mass_kg: float | None = None
    density_used: float | None = None
    source: str = "stub"  # "cad" | "stub"
    # Дерево изделия (FR-010): корневой узел; для одиночной детали — один лист.
    assembly_tree: AssemblyNode | None = None
    is_assembly: bool = False


class DataCompleteness(BaseModel):
    """Какие источники переданы и использованы ли заглушки."""

    has_drawing: bool = False
    has_model3d: bool = False
    vision_stub: bool = False
    geometry_stub: bool = False


class VerifyResult(BaseModel):
    ok: bool = True
    flags: list[str] = Field(default_factory=list)


class NormRow(BaseModel):
    num: int
    designation: str | None = None
    name: str | None = None
    material: str | None = None
    zagotovka: str | None = None
    qty_per_set: int = 1
    md_kg: float | None = None
    mz_kg: float | None = None
    kim: float | None = None
    norm_per_part_kg: float | None = None
    norm_program_kg: float | None = None
    flags: list[str] = Field(default_factory=list)


class JobResult(BaseModel):
    job_id: str
    mode: JobMode = "paired"
    data_completeness: DataCompleteness = Field(default_factory=DataCompleteness)
    extract: ExtractResult
    geometry: GeometryResult
    verify: VerifyResult
    rows: list[NormRow]
    # Отладочная информация (FR-002): координаты зон, признак формата. Только при debug=true.
    debug: dict | None = None


class NormControlRequest(BaseModel):
    rows: list[NormRow]


class NormControlResponse(BaseModel):
    flags: list[str]
    rows: list[NormRow]
