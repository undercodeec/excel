"""Ponderación estándar: peso × calificación. EFI, EFE, AOOR, MPC, Aprovechabilidad, MADI, MADE."""
from dataclasses import dataclass

TOLERANCIA_PESO = 0.01


@dataclass
class FactorPonderado:
    descripcion: str
    peso: float
    calificacion: float
    resultado: float


@dataclass
class ResultadoPonderacion:
    factores: list[FactorPonderado]
    total: float
    pesos_validos: bool
    suma_pesos: float


def validar_pesos(pesos: list[float], tolerancia: float = TOLERANCIA_PESO) -> bool:
    """Los pesos deben sumar 1.0 (±tolerancia)."""
    return abs(sum(pesos) - 1.0) <= tolerancia


def validar_calificacion(calificacion: float, minimo: int, maximo: int) -> bool:
    """La calificación debe caer dentro de la escala [minimo, maximo]."""
    return minimo <= calificacion <= maximo


def calcular(
    factores: list[dict],
    escala_min: int = 1,
    escala_max: int = 4,
) -> ResultadoPonderacion:
    """Calcula resultado_i = peso_i * calificacion_i y el total.

    Cada factor: {"descripcion": str, "peso": float, "calificacion": float}.
    Valida escala de calificación y suma de pesos.
    """
    resultados: list[FactorPonderado] = []
    for f in factores:
        peso = f["peso"]
        cal = f["calificacion"]
        if not validar_calificacion(cal, escala_min, escala_max):
            raise ValueError(
                f"Calificación {cal} fuera de escala [{escala_min}, {escala_max}] "
                f"en '{f.get('descripcion', '?')}'"
            )
        resultados.append(
            FactorPonderado(
                descripcion=f.get("descripcion", ""),
                peso=peso,
                calificacion=cal,
                resultado=round(peso * cal, 6),
            )
        )

    total = round(sum(r.resultado for r in resultados), 6)
    suma_pesos = round(sum(f["peso"] for f in factores), 6)
    return ResultadoPonderacion(
        factores=resultados,
        total=total,
        pesos_validos=validar_pesos([f["peso"] for f in factores]),
        suma_pesos=suma_pesos,
    )
