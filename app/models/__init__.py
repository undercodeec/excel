"""Registro central de modelos ORM. Importar desde aquí garantiza que todas las
relaciones queden resueltas al crear el esquema."""
from app.models.empresa import Empresa, PremisasFinancieras
from app.models.matriz import Matriz, FactorMatriz
from app.models.plan import Plan, Estrategia, Actividad, Indicador
from app.models.cmi import Perspectiva, ObjetivoCMI, IndicadorCMI, Medicion

__all__ = [
    "Empresa", "PremisasFinancieras",
    "Matriz", "FactorMatriz",
    "Plan", "Estrategia", "Actividad", "Indicador",
    "Perspectiva", "ObjetivoCMI", "IndicadorCMI", "Medicion",
]
