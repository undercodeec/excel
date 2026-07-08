"""Servicio del dashboard general: resume Matrices, Planes, KPI y CMI de una empresa."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core import semaforo
from app.models.cmi import IndicadorCMI, Medicion, ObjetivoCMI, Perspectiva
from app.models.empresa import Empresa
from app.models.matriz import Matriz
from app.models.plan import Actividad, Estrategia, Indicador, Plan
from app.schemas.dashboard import (
    DashboardGeneralRead,
    ResumenCmi,
    ResumenKpi,
    ResumenMatrices,
    ResumenPlanes,
    ResumenSemaforos,
    ResumenTrazabilidad,
)
from app.services.planes import totalizar_consolidado_empresa


def generar_dashboard_general(
    db: Session, empresa_id: int
) -> DashboardGeneralRead | None:
    """Agrega el estado de los cuatro módulos para una empresa."""
    empresa = db.get(Empresa, empresa_id)
    if empresa is None:
        return None

    return DashboardGeneralRead(
        empresa_id=empresa_id,
        empresa_nombre=empresa.nombre,
        matrices=_resumen_matrices(db, empresa_id),
        planes=_resumen_planes(db, empresa_id),
        kpi=_resumen_kpi(db, empresa_id),
        cmi=_resumen_cmi(db, empresa_id),
        trazabilidad=_resumen_trazabilidad(db, empresa_id),
    )


def _resumen_matrices(db: Session, empresa_id: int) -> ResumenMatrices:
    matrices = db.query(Matriz).filter(Matriz.empresa_id == empresa_id).all()
    por_tipo: dict[str, int] = {}
    for m in matrices:
        por_tipo[m.tipo.value] = por_tipo.get(m.tipo.value, 0) + 1
    return ResumenMatrices(total=len(matrices), por_tipo=por_tipo)


def _resumen_planes(db: Session, empresa_id: int) -> ResumenPlanes:
    consolidado = totalizar_consolidado_empresa(db, empresa_id)
    total_estrategias = (
        db.query(Estrategia)
        .join(Plan, Estrategia.plan_id == Plan.id)
        .filter(Plan.empresa_id == empresa_id)
        .count()
    )
    total_actividades = (
        db.query(Actividad)
        .join(Estrategia, Actividad.estrategia_id == Estrategia.id)
        .join(Plan, Estrategia.plan_id == Plan.id)
        .filter(Plan.empresa_id == empresa_id)
        .count()
    )
    return ResumenPlanes(
        total_planes=len(consolidado.planes),
        total_estrategias=total_estrategias,
        total_actividades=total_actividades,
        total_costo=consolidado.total_costo,
        total_por_tipo={tipo.value: costo for tipo, costo in consolidado.total_por_tipo.items()},
    )


def _resumen_kpi(db: Session, empresa_id: int) -> ResumenKpi:
    total = (
        db.query(Indicador)
        .join(Estrategia, Indicador.estrategia_id == Estrategia.id)
        .join(Plan, Estrategia.plan_id == Plan.id)
        .filter(Plan.empresa_id == empresa_id)
        .count()
    )
    return ResumenKpi(total_indicadores=total)


def _resumen_cmi(db: Session, empresa_id: int) -> ResumenCmi:
    perspectivas = (
        db.query(Perspectiva).filter(Perspectiva.empresa_id == empresa_id).all()
    )
    indicadores: list[IndicadorCMI] = []
    total_objetivos = 0
    for p in perspectivas:
        total_objetivos += len(p.objetivos)
        for o in p.objetivos:
            indicadores.extend(o.indicadores)

    semaforos = ResumenSemaforos()
    total_mediciones = 0
    for ind in indicadores:
        total_mediciones += len(ind.mediciones)
        estado = _estado_indicador(ind)
        if estado is None:
            semaforos.sin_medicion += 1
        elif estado == semaforo.Estado.VERDE:
            semaforos.verde += 1
        elif estado == semaforo.Estado.AMARILLO:
            semaforos.amarillo += 1
        else:
            semaforos.rojo += 1

    return ResumenCmi(
        total_perspectivas=len(perspectivas),
        total_objetivos=total_objetivos,
        total_indicadores=len(indicadores),
        total_mediciones=total_mediciones,
        semaforos=semaforos,
    )


def _estado_indicador(ind: IndicadorCMI) -> semaforo.Estado | None:
    """Evalúa el semáforo con la medición más reciente (mayor id)."""
    if not ind.mediciones:
        return None
    ultima = max(ind.mediciones, key=lambda m: m.id)
    resultado = semaforo.evaluar(
        valor_actual=ultima.valor,
        meta=ind.meta,
        rango_min=ind.rango_min if ind.rango_min is not None else ind.meta,
        rango_max=ind.rango_max if ind.rango_max is not None else ind.meta,
        sentido=semaforo.Sentido(ind.sentido.value),
    )
    return resultado.estado


def _resumen_trazabilidad(db: Session, empresa_id: int) -> ResumenTrazabilidad:
    estrategias_con_matriz = (
        db.query(Estrategia)
        .join(Plan, Estrategia.plan_id == Plan.id)
        .filter(Plan.empresa_id == empresa_id, Estrategia.matriz_id.isnot(None))
        .count()
    )
    indicadores_cmi_con_kpi = (
        db.query(IndicadorCMI)
        .join(ObjetivoCMI, IndicadorCMI.objetivo_id == ObjetivoCMI.id)
        .join(Perspectiva, ObjetivoCMI.perspectiva_id == Perspectiva.id)
        .filter(Perspectiva.empresa_id == empresa_id, IndicadorCMI.kpi_id.isnot(None))
        .count()
    )
    return ResumenTrazabilidad(
        estrategias_con_matriz=estrategias_con_matriz,
        indicadores_cmi_con_kpi=indicadores_cmi_con_kpi,
    )
