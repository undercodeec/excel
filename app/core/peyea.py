"""PEYEA: 4 dimensiones (FF, FI, EE, VC) → ejes X/Y y cuadrante."""
from dataclasses import dataclass

# FF y FI usan calificaciones positivas (+1..+6 / +1..+5 según formato)
# EE y VC usan calificaciones negativas (-1..-6 / -1..-5)


@dataclass
class ResultadoPeyea:
    ff: float          # Fuerza Financiera (promedio, positivo)
    fi: float          # Fuerza de la Industria (positivo)
    ee: float          # Estabilidad del Entorno (negativo)
    vc: float          # Ventaja Competitiva (negativo)
    x: float           # FI + VC
    y: float           # FF + EE
    cuadrante: str


def _promedio(calificaciones: list[float]) -> float:
    if not calificaciones:
        return 0.0
    return round(sum(calificaciones) / len(calificaciones), 6)


def _cuadrante(x: float, y: float) -> str:
    if x >= 0 and y >= 0:
        return "Agresivo"
    if x < 0 and y >= 0:
        return "Conservador"
    if x < 0 and y < 0:
        return "Defensivo"
    return "Competitivo"  # x>=0, y<0


def calcular(
    ff: list[float],
    fi: list[float],
    ee: list[float],
    vc: list[float],
) -> ResultadoPeyea:
    """Cada dimensión es una lista de calificaciones; se promedian.

    FF, FI: positivas. EE, VC: negativas.
    Eje X = FI + VC ; Eje Y = FF + EE.
    """
    prom_ff = _promedio(ff)
    prom_fi = _promedio(fi)
    prom_ee = _promedio(ee)
    prom_vc = _promedio(vc)

    x = round(prom_fi + prom_vc, 6)
    y = round(prom_ff + prom_ee, 6)
    return ResultadoPeyea(
        ff=prom_ff, fi=prom_fi, ee=prom_ee, vc=prom_vc,
        x=x, y=y, cuadrante=_cuadrante(x, y),
    )
