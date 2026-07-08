"""Schemas de trazabilidad: Matriz → Estrategia → Plan → KPI → Indicador CMI."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TipoMatriz, TipoPlan


class MatrizOrigenRead(BaseModel):
    """Matriz de diagnóstico de la que nace la estrategia."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: TipoMatriz
    nombre: str


class PlanTrazaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: TipoPlan
    empresa_id: int


class IndicadorCMITrazaRead(BaseModel):
    """Indicador de control (CMI) vinculado a un KPI táctico."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    meta: float
    objetivo_id: int


class KpiTrazaRead(BaseModel):
    """KPI táctico de la estrategia con sus indicadores de control CMI."""
    id: int
    nombre: str
    formula: str | None = None
    frecuencia: str | None = None
    ponderacion: float | None = None
    indicadores_cmi: list[IndicadorCMITrazaRead] = Field(default_factory=list)


class TrazabilidadEstrategiaRead(BaseModel):
    """Cadena completa desde una estrategia hacia su origen y su control."""
    estrategia_id: int
    tipo_estrategia: str | None = None
    descripcion: str
    matriz_origen: MatrizOrigenRead | None = None
    plan: PlanTrazaRead
    kpis: list[KpiTrazaRead] = Field(default_factory=list)
