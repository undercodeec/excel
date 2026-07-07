"""Semáforos CMI: evalúa VERDE/AMARILLO/ROJO con sentido directo o inverso."""
from dataclasses import dataclass
from enum import Enum


class Estado(str, Enum):
    VERDE = "VERDE"
    AMARILLO = "AMARILLO"
    ROJO = "ROJO"


class Sentido(str, Enum):
    DIRECTO = "directo"    # mayor es mejor
    INVERSO = "inverso"    # menor es mejor (# quejas, % NC)


@dataclass
class ResultadoSemaforo:
    valor_actual: float
    meta: float
    cumplimiento: float | None
    estado: Estado
    sentido: Sentido


def evaluar(
    valor_actual: float,
    meta: float,
    rango_min: float,
    rango_max: float,
    sentido: Sentido = Sentido.DIRECTO,
) -> ResultadoSemaforo:
    """Evalúa el estado del indicador.

    rango_min/rango_max delimitan la zona AMARILLA (alerta).
    - Directo: VERDE si valor >= meta; ROJO si valor < rango_min; AMARILLO en medio.
    - Inverso: VERDE si valor <= meta; ROJO si valor > rango_max; AMARILLO en medio.
    """
    cumplimiento = None if meta == 0 else round(valor_actual / meta, 6)

    if sentido == Sentido.DIRECTO:
        if valor_actual >= meta:
            estado = Estado.VERDE
        elif valor_actual < rango_min:
            estado = Estado.ROJO
        else:
            estado = Estado.AMARILLO
    else:  # INVERSO
        if valor_actual <= meta:
            estado = Estado.VERDE
        elif valor_actual > rango_max:
            estado = Estado.ROJO
        else:
            estado = Estado.AMARILLO

    return ResultadoSemaforo(
        valor_actual=valor_actual,
        meta=meta,
        cumplimiento=cumplimiento,
        estado=estado,
        sentido=sentido,
    )
