"""Schemas Pydantic para Empresa."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EmpresaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    mision: str | None = None
    vision: str | None = None
    periodo: str | None = Field(default=None, max_length=50)
    moneda: str | None = Field(default=None, max_length=10)


class EmpresaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    mision: str | None = None
    vision: str | None = None
    periodo: str | None = None
    moneda: str
