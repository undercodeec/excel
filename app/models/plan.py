"""Modelo Plan → Estrategia → Actividad, e Indicador (KPI) por estrategia."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TipoPlan


class Plan(Base):
    __tablename__ = "plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"))
    tipo: Mapped[TipoPlan] = mapped_column(SAEnum(TipoPlan))

    empresa: Mapped["Empresa"] = relationship(back_populates="planes")
    estrategias: Mapped[list["Estrategia"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )


class Estrategia(Base):
    __tablename__ = "estrategia"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan.id"))
    # Trazabilidad: matriz de diagnóstico de la que nace la estrategia (opcional).
    matriz_id: Mapped[int | None] = mapped_column(ForeignKey("matriz.id"), default=None)
    tipo_estrategia: Mapped[str | None] = mapped_column(String(200), default=None)
    descripcion: Mapped[str] = mapped_column(String(400))

    plan: Mapped["Plan"] = relationship(back_populates="estrategias")
    matriz: Mapped["Matriz | None"] = relationship()
    actividades: Mapped[list["Actividad"]] = relationship(
        back_populates="estrategia", cascade="all, delete-orphan"
    )
    indicadores: Mapped[list["Indicador"]] = relationship(
        back_populates="estrategia", cascade="all, delete-orphan"
    )


class Actividad(Base):
    __tablename__ = "actividad"

    id: Mapped[int] = mapped_column(primary_key=True)
    estrategia_id: Mapped[int] = mapped_column(ForeignKey("estrategia.id"))
    descripcion: Mapped[str] = mapped_column(String(400))
    responsable: Mapped[str | None] = mapped_column(String(200), default=None)
    tiempo: Mapped[str | None] = mapped_column(String(100), default=None)
    costo: Mapped[float | None] = mapped_column(Float, default=None)
    tipo_cuenta: Mapped[str | None] = mapped_column(String(100), default=None)

    estrategia: Mapped["Estrategia"] = relationship(back_populates="actividades")


class Indicador(Base):
    """KPI táctico ligado a una estrategia."""
    __tablename__ = "indicador"

    id: Mapped[int] = mapped_column(primary_key=True)
    estrategia_id: Mapped[int] = mapped_column(ForeignKey("estrategia.id"))
    tipo: Mapped[str | None] = mapped_column(String(100), default=None)
    nombre: Mapped[str] = mapped_column(String(300))
    formula: Mapped[str | None] = mapped_column(String(400), default=None)
    frecuencia: Mapped[str | None] = mapped_column(String(50), default=None)
    ponderacion: Mapped[float | None] = mapped_column(Float, default=None)

    estrategia: Mapped["Estrategia"] = relationship(back_populates="indicadores")


from app.models.empresa import Empresa  # noqa: E402
from app.models.matriz import Matriz  # noqa: E402
