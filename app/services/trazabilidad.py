"""Servicio de trazabilidad: reconstruye la cadena Matriz → Estrategia → Plan → KPI → CMI."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.cmi import IndicadorCMI
from app.models.empresa import Empresa
from app.models.matriz import Matriz
from app.models.plan import Estrategia
from app.schemas.trazabilidad import (
    ActividadTrazaRead,
    EmpresaInformeRead,
    EstrategiaVinculadaRead,
    IndicadorCMITrazaRead,
    InformeMatrizRead,
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


def trazar_matriz(db: Session, matriz_id: int) -> InformeMatrizRead | None:
    """Devuelve el informe completo de una matriz: empresa, cálculo y estrategias vinculadas."""
    from app.services.matrices import calcular_matriz

    matriz = db.get(Matriz, matriz_id)
    if matriz is None:
        return None

    empresa = db.get(Empresa, matriz.empresa_id)
    if empresa is None:
        return None

    try:
        calculo = calcular_matriz(db, matriz_id)
    except ValueError:
        calculo = {}

    estrategias_db = db.query(Estrategia).filter(Estrategia.matriz_id == matriz_id).all()

    estrategias_vinculadas: list[EstrategiaVinculadaRead] = []
    for est in estrategias_db:
        actividades = [ActividadTrazaRead.model_validate(a) for a in est.actividades]

        kpis: list[KpiTrazaRead] = []
        for kpi in est.indicadores:
            indicadores_cmi = db.query(IndicadorCMI).filter(IndicadorCMI.kpi_id == kpi.id).all()
            kpis.append(
                KpiTrazaRead(
                    id=kpi.id,
                    nombre=kpi.nombre,
                    formula=kpi.formula,
                    frecuencia=kpi.frecuencia,
                    ponderacion=kpi.ponderacion,
                    indicadores_cmi=[IndicadorCMITrazaRead.model_validate(i) for i in indicadores_cmi],
                )
            )

        estrategias_vinculadas.append(
            EstrategiaVinculadaRead(
                estrategia_id=est.id,
                descripcion=est.descripcion,
                tipo_estrategia=est.tipo_estrategia,
                plan_id=est.plan_id,
                plan_tipo=est.plan.tipo,
                actividades=actividades,
                kpis=kpis,
            )
        )

    return InformeMatrizRead(
        empresa=EmpresaInformeRead(
            id=empresa.id,
            nombre=empresa.nombre,
            mision=empresa.mision,
            vision=empresa.vision,
            periodo=empresa.periodo,
            moneda=empresa.moneda,
        ),
        matriz_id=matriz.id,
        matriz_nombre=matriz.nombre,
        matriz_tipo=matriz.tipo,
        calculo=calculo,
        estrategias_vinculadas=estrategias_vinculadas,
    )
