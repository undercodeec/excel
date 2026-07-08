"""Modelo de usuarios para autenticacion basica por empresa."""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresa.id"))
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    nombre: Mapped[str | None] = mapped_column(String(200), default=None)
    password_hash: Mapped[str] = mapped_column(String(255))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    empresa: Mapped["Empresa"] = relationship(back_populates="usuarios")


from app.models.empresa import Empresa  # noqa: E402
