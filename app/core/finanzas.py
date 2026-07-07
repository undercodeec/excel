"""Finanzas: proyección 5 años, VAN, TIR, payback, punto de equilibrio."""
from dataclasses import dataclass

import numpy_financial as npf

# Premisas por defecto (§5.5 / §10)
INFLACION = 0.04
CRECIMIENTO_VENTAS = 0.08
IMPUESTOS = 0.36
WACC = 0.12


@dataclass
class AnioProyeccion:
    anio: int
    ventas: float
    costos: float
    utilidad_bruta: float
    gastos_operativos: float
    ebitda: float
    utilidad_neta: float


@dataclass
class ResultadoProyeccion:
    anios: list[AnioProyeccion]


def proyectar(
    ventas_0: float,
    costos_0: float,
    gastos_operativos_0: float,
    anios: int = 5,
    crecimiento_ventas: float = CRECIMIENTO_VENTAS,
    inflacion: float = INFLACION,
    impuestos: float = IMPUESTOS,
) -> ResultadoProyeccion:
    """Proyección compuesta. El año base (0) crece durante `anios` periodos."""
    resultado: list[AnioProyeccion] = []
    ventas = ventas_0
    costos = costos_0
    gastos = gastos_operativos_0
    for n in range(1, anios + 1):
        ventas = ventas * (1 + crecimiento_ventas)
        costos = costos * (1 + inflacion)
        gastos = gastos * (1 + inflacion)
        utilidad_bruta = ventas - costos
        ebitda = utilidad_bruta - gastos
        utilidad_neta = ebitda * (1 - impuestos)
        resultado.append(
            AnioProyeccion(
                anio=n,
                ventas=round(ventas, 2),
                costos=round(costos, 2),
                utilidad_bruta=round(utilidad_bruta, 2),
                gastos_operativos=round(gastos, 2),
                ebitda=round(ebitda, 2),
                utilidad_neta=round(utilidad_neta, 2),
            )
        )
    return ResultadoProyeccion(anios=resultado)


def van(inversion_inicial: float, flujos: list[float], wacc: float = WACC) -> float:
    """VAN con inversión inicial negativa en el periodo 0.

    npf.npv(rate, [f0, f1, ...]) descuenta f0 en t=0.
    """
    serie = [-abs(inversion_inicial)] + list(flujos)
    return round(float(npf.npv(wacc, serie)), 3)


def tir(inversion_inicial: float, flujos: list[float]) -> float:
    """TIR (fracción). Devolver como decimal; multiplicar por 100 para %."""
    serie = [-abs(inversion_inicial)] + list(flujos)
    return round(float(npf.irr(serie)), 6)


def payback(inversion_inicial: float, flujos: list[float]) -> float | None:
    """Años (con fracción por interpolación) hasta recuperar la inversión.

    None si nunca se recupera dentro del horizonte.
    """
    objetivo = abs(inversion_inicial)
    acumulado = 0.0
    for i, flujo in enumerate(flujos, start=1):
        anterior = acumulado
        acumulado += flujo
        if acumulado >= objetivo:
            faltante = objetivo - anterior
            fraccion = faltante / flujo if flujo else 0.0
            return round((i - 1) + fraccion, 4)
    return None


def punto_equilibrio(costos_fijos: float, costos_variables: float, ventas: float) -> float:
    """PE = Costos fijos / (1 − Costos variables / Ventas)."""
    if ventas == 0:
        raise ValueError("Ventas no puede ser 0 para el punto de equilibrio.")
    margen = 1 - (costos_variables / ventas)
    if margen == 0:
        raise ValueError("Margen de contribución 0; punto de equilibrio indefinido.")
    return round(costos_fijos / margen, 2)
