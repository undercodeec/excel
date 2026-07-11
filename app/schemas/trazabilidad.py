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


# ---------- Schemas para informe de matriz ----------

class EmpresaInformeRead(BaseModel):
    """Datos de la empresa que contextualiza la matriz."""
    id: int
    nombre: str
    mision: str | None = None
    vision: str | None = None
    periodo: str | None = None
    moneda: str = "USD"


class ActividadTrazaRead(BaseModel):
    """Actividad derivada de una estrategia vinculada a la matriz."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    descripcion: str
    responsable: str | None = None
    tiempo: str | None = None
    costo: float | None = None
    tipo_cuenta: str | None = None


class EstrategiaVinculadaRead(BaseModel):
    """Estrategia que nació de esta matriz, con su plan y actividades."""
    estrategia_id: int
    descripcion: str
    tipo_estrategia: str | None = None
    plan_id: int
    plan_tipo: TipoPlan
    actividades: list[ActividadTrazaRead] = Field(default_factory=list)
    kpis: list[KpiTrazaRead] = Field(default_factory=list)


class InformeMatrizRead(BaseModel):
    """Informe completo de una matriz: empresa + cálculo + estrategias vinculadas."""
    empresa: EmpresaInformeRead
    matriz_id: int
    matriz_nombre: str
    matriz_tipo: TipoMatriz
    calculo: dict
    estrategias_vinculadas: list[EstrategiaVinculadaRead] = Field(default_factory=list)
