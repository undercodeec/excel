"""Schemas del dashboard general: resumen agregado de los 4 módulos por empresa."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ResumenMatrices(BaseModel):
    total: int = 0
    por_tipo: dict[str, int] = Field(default_factory=dict)


class ResumenPlanes(BaseModel):
    total_planes: int = 0
    total_estrategias: int = 0
    total_actividades: int = 0
    total_costo: float = 0.0
    total_por_tipo: dict[str, float] = Field(default_factory=dict)


class ResumenKpi(BaseModel):
    total_indicadores: int = 0


class ResumenSemaforos(BaseModel):
    verde: int = 0
    amarillo: int = 0
    rojo: int = 0
    sin_medicion: int = 0


class ResumenCmi(BaseModel):
    total_perspectivas: int = 0
    total_objetivos: int = 0
    total_indicadores: int = 0
    total_mediciones: int = 0
    semaforos: ResumenSemaforos = Field(default_factory=ResumenSemaforos)


class ResumenTrazabilidad(BaseModel):
    estrategias_con_matriz: int = 0
    indicadores_cmi_con_kpi: int = 0


class DashboardGeneralRead(BaseModel):
    empresa_id: int
    empresa_nombre: str
    matrices: ResumenMatrices
    planes: ResumenPlanes
    kpi: ResumenKpi
    cmi: ResumenCmi
    trazabilidad: ResumenTrazabilidad
