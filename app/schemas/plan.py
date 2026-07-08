"""Schemas Pydantic para Planes, Estrategias y Actividades."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TipoPeriodo, TipoPlan


class ActividadBase(BaseModel):
    descripcion: str = Field(min_length=1, max_length=400)
    responsable: str | None = Field(default=None, max_length=200)
    tiempo: str | None = Field(default=None, max_length=100)
    costo: float | None = Field(default=None, ge=0)
    tipo_cuenta: str | None = Field(default=None, max_length=100)


class ActividadCreate(ActividadBase):
    pass


class ActividadUpdate(BaseModel):
    descripcion: str | None = Field(default=None, min_length=1, max_length=400)
    responsable: str | None = Field(default=None, max_length=200)
    tiempo: str | None = Field(default=None, max_length=100)
    costo: float | None = Field(default=None, ge=0)
    tipo_cuenta: str | None = Field(default=None, max_length=100)


class ActividadRead(ActividadBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    estrategia_id: int


class IndicadorBase(BaseModel):
    tipo: str | None = Field(default=None, max_length=100)
    nombre: str = Field(min_length=1, max_length=300)
    formula: str | None = Field(default=None, max_length=400)
    frecuencia: str | None = Field(default=None, max_length=50)
    ponderacion: float | None = Field(default=None, ge=0, le=1)


class IndicadorCreate(IndicadorBase):
    pass


class IndicadorUpdate(BaseModel):
    tipo: str | None = Field(default=None, max_length=100)
    nombre: str | None = Field(default=None, min_length=1, max_length=300)
    formula: str | None = Field(default=None, max_length=400)
    frecuencia: str | None = Field(default=None, max_length=50)
    ponderacion: float | None = Field(default=None, ge=0, le=1)


class IndicadorRead(IndicadorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    estrategia_id: int


class PonderacionesTacticasRead(BaseModel):
    estrategia_id: int
    total_ponderacion: float
    diferencia: float
    valido: bool
    indicadores: list[IndicadorRead] = Field(default_factory=list)


class CalculoKpiCreate(BaseModel):
    numerador: float
    denominador: float
    periodo: str | None = Field(default=None, max_length=50)
    tipo_periodo: TipoPeriodo | None = None


class CalculoKpiRead(BaseModel):
    indicador_id: int
    nombre: str
    frecuencia: str | None = None
    periodo: str | None = None
    tipo_periodo: TipoPeriodo | None = None
    numerador: float
    denominador: float
    valor: float | None
    formula: str


class EstrategiaBase(BaseModel):
    tipo_estrategia: str | None = Field(default=None, max_length=200)
    descripcion: str = Field(min_length=1, max_length=400)
    matriz_id: int | None = None  # trazabilidad: matriz de diagnóstico origen


class EstrategiaCreate(EstrategiaBase):
    actividades: list[ActividadCreate] = Field(default_factory=list)
    indicadores: list[IndicadorCreate] = Field(default_factory=list)


class EstrategiaUpdate(BaseModel):
    tipo_estrategia: str | None = Field(default=None, max_length=200)
    descripcion: str | None = Field(default=None, min_length=1, max_length=400)
    matriz_id: int | None = None


class EstrategiaRead(EstrategiaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plan_id: int
    actividades: list[ActividadRead] = Field(default_factory=list)
    indicadores: list[IndicadorRead] = Field(default_factory=list)


class PlanBase(BaseModel):
    tipo: TipoPlan


class PlanCreate(PlanBase):
    empresa_id: int
    estrategias: list[EstrategiaCreate] = Field(default_factory=list)


class PlanUpdate(BaseModel):
    tipo: TipoPlan | None = None


class PlanRead(PlanBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empresa_id: int
    estrategias: list[EstrategiaRead] = Field(default_factory=list)


class ActividadTotalRead(BaseModel):
    id: int
    descripcion: str
    costo: float
    tipo_cuenta: str | None = None


class EstrategiaTotalRead(BaseModel):
    id: int
    tipo_estrategia: str | None = None
    descripcion: str
    total_costo: float
    actividades: list[ActividadTotalRead] = Field(default_factory=list)


class PlanTotalRead(BaseModel):
    plan_id: int
    empresa_id: int
    tipo: TipoPlan
    total_costo: float
    estrategias: list[EstrategiaTotalRead] = Field(default_factory=list)


class ConsolidadoPlanesRead(BaseModel):
    empresa_id: int
    total_costo: float
    total_por_tipo: dict[TipoPlan, float]
    planes: list[PlanTotalRead] = Field(default_factory=list)


class PremisasFinancierasRead(BaseModel):
    inflacion: float
    crecimiento_ventas: float
    impuestos: float
    wacc: float


class AnioFinancieroRead(BaseModel):
    anio: int
    ventas: float
    costos: float
    utilidad_bruta: float
    gastos_operativos: float
    ebitda: float
    utilidad_neta: float


class MetricasFinancierasRead(BaseModel):
    van: float
    tir: float | None
    payback: float | None
    punto_equilibrio: float | None


class DashboardFinancieroRead(BaseModel):
    empresa_id: int
    ventas_base: float
    costos_base: float
    gastos_operativos_base: float
    inversion_inicial: float
    total_planes: float
    premisas: PremisasFinancierasRead
    proyeccion: list[AnioFinancieroRead]
    flujos: list[float]
    metricas: MetricasFinancierasRead
