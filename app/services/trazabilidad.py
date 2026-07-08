"""Servicio de trazabilidad: reconstruye la cadena Matriz → Estrategia → Plan → KPI → CMI."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.cmi import IndicadorCMI
from app.models.plan import Estrategia
from app.schemas.trazabilidad import (
    IndicadorCMITrazaRead,
    KpiTrazaRead,
    MatrizOrigenRead,
    PlanTrazaRead,
    TrazabilidadEstrategiaRead,
)


def trazar_estrategia(
    db: Session, estrategia_id: int
) -> TrazabilidadEstrategiaRead | None:
    """Devuelve la cadena de trazabilidad partiendo de una estrategia.

    Enlaza hacia atrás con la matriz de diagnóstico y el plan, y hacia adelante
    con los KPI tácticos y los indicadores de control (CMI) que los miden.
    """
    estrategia = db.get(Estrategia, estrategia_id)
    if estrategia is None:
        return None

    matriz_origen = (
        MatrizOrigenRead.model_validate(estrategia.matriz)
        if estrategia.matriz is not None
        else None
    )

    kpis: list[KpiTrazaRead] = []
    for kpi in estrategia.indicadores:
        indicadores_cmi = (
            db.query(IndicadorCMI).filter(IndicadorCMI.kpi_id == kpi.id).all()
        )
        kpis.append(
            KpiTrazaRead(
                id=kpi.id,
                nombre=kpi.nombre,
                formula=kpi.formula,
                frecuencia=kpi.frecuencia,
                ponderacion=kpi.ponderacion,
                indicadores_cmi=[
                    IndicadorCMITrazaRead.model_validate(ind) for ind in indicadores_cmi
                ],
            )
        )

    return TrazabilidadEstrategiaRead(
        estrategia_id=estrategia.id,
        tipo_estrategia=estrategia.tipo_estrategia,
        descripcion=estrategia.descripcion,
        matriz_origen=matriz_origen,
        plan=PlanTrazaRead.model_validate(estrategia.plan),
        kpis=kpis,
    )
