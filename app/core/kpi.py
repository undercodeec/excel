"""KPI: valor = numerador / denominador y validación de ponderaciones tácticas."""
from dataclasses import dataclass

TOLERANCIA_PONDERACION = 0.01


@dataclass
class ResultadoKpi:
    nombre: str
    numerador: float
    denominador: float
    valor: float | None
    formula: str


def calcular_kpi(
    nombre: str,
    numerador: float,
    denominador: float,
    formula: str = "",
) -> ResultadoKpi:
    """valor = numerador / denominador; división por cero → None."""
    valor = None if denominador == 0 else round(numerador / denominador, 6)
    return ResultadoKpi(
        nombre=nombre,
        numerador=numerador,
        denominador=denominador,
        valor=valor,
        formula=formula or f"({numerador} / {denominador})",
    )


def validar_ponderaciones(ponderaciones: list[float], tolerancia: float = TOLERANCIA_PONDERACION) -> bool:
    """El conjunto de ponderaciones tácticas debe sumar ~1.0."""
    return abs(sum(ponderaciones) - 1.0) <= tolerancia
