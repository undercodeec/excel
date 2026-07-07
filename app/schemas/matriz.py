"""Schemas Pydantic para Matrices: validación de pesos (suma≈1) y escalas."""
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict, model_validator

from app.models.enums import TipoMatriz

TOLERANCIA_PESO = 0.01

# Escalas de calificación por tipo de matriz (min, max)
ESCALAS: dict[TipoMatriz, tuple[int, int]] = {
    TipoMatriz.efi: (1, 4),
    TipoMatriz.efe: (1, 4),
    TipoMatriz.madi: (1, 4),
    TipoMatriz.made: (1, 4),
    TipoMatriz.aoor: (1, 4),
    TipoMatriz.aprovechabilidad: (1, 5),
    TipoMatriz.mpc: (1, 5),
}

# Tipos que exigen pesos que sumen 1
TIPOS_PONDERADOS = set(ESCALAS.keys())


# ---------- Factores ----------
class FactorBase(BaseModel):
    descripcion: str = Field(min_length=1, max_length=300)
    peso: float | None = Field(default=None, ge=0, le=1)
    calificacion: float | None = None
    extra_json: dict | None = None


class FactorCreate(FactorBase):
    pass


class FactorRead(FactorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    resultado: float | None = None


# ---------- Matriz ----------
class MatrizBase(BaseModel):
    tipo: TipoMatriz
    nombre: str = Field(min_length=1, max_length=200)


class MatrizCreate(MatrizBase):
    empresa_id: int
    factores: list[FactorCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validar_pesos_y_escalas(self) -> "MatrizCreate":
        escala = ESCALAS.get(self.tipo)
        # Validar escala de calificación
        if escala:
            lo, hi = escala
            for f in self.factores:
                if f.calificacion is not None and not (lo <= f.calificacion <= hi):
                    raise ValueError(
                        f"Calificación {f.calificacion} fuera de escala [{lo},{hi}] "
                        f"para tipo '{self.tipo.value}' en '{f.descripcion}'."
                    )
        # Validar suma de pesos en tipos ponderados
        if self.tipo in TIPOS_PONDERADOS and self.factores:
            pesos = [f.peso for f in self.factores if f.peso is not None]
            if len(pesos) == len(self.factores):
                if abs(sum(pesos) - 1.0) > TOLERANCIA_PESO:
                    raise ValueError(
                        f"Los pesos deben sumar 1.0 (±{TOLERANCIA_PESO}); suman {sum(pesos):.4f}."
                    )
        return self


class MatrizUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)


class MatrizRead(MatrizBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empresa_id: int
    factores: list[FactorRead] = Field(default_factory=list)
