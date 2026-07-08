"""Configuración central: URL de BD y premisas financieras por defecto."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    database_url: str = "sqlite:///./planificacion.db"

    # Aplicación
    app_name: str = "Planificación Estratégica — Hacienda Celia María C.A."

    # Premisas financieras por defecto (§10 del plan)
    secret_key: str = "dev-secret-change-me"
    inflacion: float = 0.04           # 4%
    crecimiento_ventas: float = 0.08  # 8%
    impuestos: float = 0.36           # 36%
    wacc: float = 0.12                # 12%


settings = Settings()
