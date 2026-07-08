"""Modelo Empresa (raíz) y PremisasFinancieras."""
from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Empresa(Base):
    __tablename__ = "empresa"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    mision: Mapped[str | None] = mapped_column(Text, default=None)
    vision: Mapped[str | None] = mapped_column(Text, default=None)
    periodo: Mapped[str | None] = mapped_column(String(50), default=None)
    moneda: Mapped[str] = mapped_column(String(10), default="USD")

    matrices: Mapped[list["Matriz"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")
    planes: Mapped[list["Plan"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")
    perspectivas: Mapped[list["Perspectiva"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="empresa", cascade="all, delete-orphan")
    premisas: Mapped["PremisasFinancieras | None"] = relationship(
        back_populates="empresa", cascade="all, delete-orphan", uselist=False
    )


class PremisasFinancieras(Base):
    __tablename__ = "premisas_financieras"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"))
    inflacion: Mapped[float] = mapped_column(Float, default=0.04)
    crecimiento_ventas: Mapped[float] = mapped_column(Float, default=0.08)
    impuestos: Mapped[float] = mapped_column(Float, default=0.36)
    wacc: Mapped[float] = mapped_column(Float, default=0.12)

    empresa: Mapped["Empresa"] = relationship(back_populates="premisas")


# Import tardío para resolver relaciones al construir el registry
from app.models.matriz import Matriz  # noqa: E402
from app.models.plan import Plan  # noqa: E402
from app.models.cmi import Perspectiva  # noqa: E402
from app.models.auth import Usuario  # noqa: E402
