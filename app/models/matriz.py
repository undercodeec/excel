"""Modelo Matriz y FactorMatriz."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Float, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TipoMatriz


class Matriz(Base):
    __tablename__ = "matriz"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"))
    tipo: Mapped[TipoMatriz] = mapped_column(SAEnum(TipoMatriz))
    nombre: Mapped[str] = mapped_column(String(200))

    empresa: Mapped["Empresa"] = relationship(back_populates="matrices")
    factores: Mapped[list["FactorMatriz"]] = relationship(
        back_populates="matriz", cascade="all, delete-orphan"
    )


class FactorMatriz(Base):
    __tablename__ = "factor_matriz"

    id: Mapped[int] = mapped_column(primary_key=True)
    matriz_id: Mapped[int] = mapped_column(ForeignKey("matriz.id"))
    descripcion: Mapped[str] = mapped_column(String(300))
    peso: Mapped[float | None] = mapped_column(Float, default=None)
    calificacion: Mapped[float | None] = mapped_column(Float, default=None)
    resultado: Mapped[float | None] = mapped_column(Float, default=None)
    # Campos específicos por tipo (coordenadas PEYEA, matriz pareada Holmes, etc.)
    extra_json: Mapped[dict | None] = mapped_column(JSON, default=None)

    matriz: Mapped["Matriz"] = relationship(back_populates="factores")


from app.models.empresa import Empresa  # noqa: E402
