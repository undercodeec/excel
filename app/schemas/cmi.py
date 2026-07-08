"""Schemas Pydantic para Cuadro de Mando Integral."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Sentido, TipoPeriodo, TipoPerspectiva


class MedicionBase(BaseModel):
    periodo: str = Field(min_length=1, max_length=50)
    tipo_periodo: TipoPeriodo = TipoPeriodo.mensual
    valor: float


class MedicionCreate(MedicionBase):
    pass


class MedicionUpdate(BaseModel):
    periodo: str | None = Field(default=None, min_length=1, max_length=50)
    tipo_periodo: TipoPeriodo | None = None
    valor: float | None = None


class MedicionRead(MedicionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    indicador_id: int


class SemaforoCMIRead(BaseModel):
    indicador_id: int
    medicion_id: int
    periodo: str
    valor_actual: float
    meta: float
    cumplimiento: float | None
    estado: str
    sentido: Sentido


class IndicadorCMIBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=300)
    meta: float
    ponderacion: float | None = Field(default=None, ge=0, le=1)
    rango_min: float | None = None
    rango_max: float | None = None
    sentido: Sentido = Sentido.directo
    kpi_id: int | None = None  # trazabilidad: KPI táctico que este indicador controla


class IndicadorCMICreate(IndicadorCMIBase):
    mediciones: list[MedicionCreate] = Field(default_factory=list)


class IndicadorCMIUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=300)
    meta: float | None = None
    ponderacion: float | None = Field(default=None, ge=0, le=1)
    rango_min: float | None = None
    rango_max: float | None = None
    sentido: Sentido | None = None
    kpi_id: int | None = None


class IndicadorCMIRead(IndicadorCMIBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    objetivo_id: int
    mediciones: list[MedicionRead] = Field(default_factory=list)


class ObjetivoCMIBase(BaseModel):
    descripcion: str = Field(min_length=1, max_length=400)


class ObjetivoCMICreate(ObjetivoCMIBase):
    indicadores: list[IndicadorCMICreate] = Field(default_factory=list)


class ObjetivoCMIUpdate(BaseModel):
    descripcion: str | None = Field(default=None, min_length=1, max_length=400)


class ObjetivoCMIRead(ObjetivoCMIBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    perspectiva_id: int
    indicadores: list[IndicadorCMIRead] = Field(default_factory=list)


class PerspectivaBase(BaseModel):
    tipo: TipoPerspectiva
    nombre: str = Field(min_length=1, max_length=200)


class PerspectivaCreate(PerspectivaBase):
    empresa_id: int
    objetivos: list[ObjetivoCMICreate] = Field(default_factory=list)


class PerspectivaUpdate(BaseModel):
    tipo: TipoPerspectiva | None = None
    nombre: str | None = Field(default=None, min_length=1, max_length=200)


class PerspectivaRead(PerspectivaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empresa_id: int
    objetivos: list[ObjetivoCMIRead] = Field(default_factory=list)
