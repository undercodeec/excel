"""Modelo CMI: Perspectiva → ObjetivoCMI → IndicadorCMI → Medicion."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TipoPerspectiva, Sentido, TipoPeriodo


class Perspectiva(Base):
    __tablename__ = "perspectiva"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"))
    tipo: Mapped[TipoPerspectiva] = mapped_column(SAEnum(TipoPerspectiva))
    nombre: Mapped[str] = mapped_column(String(200))

    empresa: Mapped["Empresa"] = relationship(back_populates="perspectivas")
    objetivos: Mapped[list["ObjetivoCMI"]] = relationship(
        back_populates="perspectiva", cascade="all, delete-orphan"
    )


class ObjetivoCMI(Base):
    __tablename__ = "objetivo_cmi"

    id: Mapped[int] = mapped_column(primary_key=True)
    perspectiva_id: Mapped[int] = mapped_column(ForeignKey("perspectiva.id"))
    descripcion: Mapped[str] = mapped_column(String(400))

    perspectiva: Mapped["Perspectiva"] = relationship(back_populates="objetivos")
    indicadores: Mapped[list["IndicadorCMI"]] = relationship(
        back_populates="objetivo", cascade="all, delete-orphan"
    )


class IndicadorCMI(Base):
    __tablename__ = "indicador_cmi"

    id: Mapped[int] = mapped_column(primary_key=True)
    objetivo_id: Mapped[int] = mapped_column(ForeignKey("objetivo_cmi.id"))
    # Trazabilidad: KPI táctico (Indicador de plan) que este indicador de control mide (opcional).
    kpi_id: Mapped[int | None] = mapped_column(ForeignKey("indicador.id"), default=None)
    nombre: Mapped[str] = mapped_column(String(300))
    meta: Mapped[float] = mapped_column(Float)
    ponderacion: Mapped[float | None] = mapped_column(Float, default=None)
    rango_min: Mapped[float | None] = mapped_column(Float, default=None)
    rango_max: Mapped[float | None] = mapped_column(Float, default=None)
    sentido: Mapped[Sentido] = mapped_column(SAEnum(Sentido), default=Sentido.directo)

    objetivo: Mapped["ObjetivoCMI"] = relationship(back_populates="indicadores")
    kpi: Mapped["Indicador | None"] = relationship()
    mediciones: Mapped[list["Medicion"]] = relationship(
        back_populates="indicador", cascade="all, delete-orphan"
    )


class Medicion(Base):
    __tablename__ = "medicion"

    id: Mapped[int] = mapped_column(primary_key=True)
    indicador_id: Mapped[int] = mapped_column(ForeignKey("indicador_cmi.id"))
    periodo: Mapped[str] = mapped_column(String(50))  # flexible: "2026-Q1", "Cosecha-1"
    tipo_periodo: Mapped[TipoPeriodo] = mapped_column(SAEnum(TipoPeriodo), default=TipoPeriodo.mensual)
    valor: Mapped[float] = mapped_column(Float)

    indicador: Mapped["IndicadorCMI"] = relationship(back_populates="mediciones")


from app.models.empresa import Empresa  # noqa: E402
from app.models.plan import Indicador  # noqa: E402
