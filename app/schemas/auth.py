"""Schemas de autenticacion."""
from pydantic import BaseModel, ConfigDict


class UsuarioSesionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    empresa_id: int
    username: str
    nombre: str | None = None
