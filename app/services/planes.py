"""Servicio de Planes: CRUD de planes, estrategias y actividades."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.config import settings
from app.core import finanzas
from app.core import kpi as kpi_core
from app.models.empresa import Empresa
from app.models.plan import Actividad, Estrategia, Indicador, Plan
from app.schemas.plan import (
    ActividadCreate,
    ActividadUpdate,
    CalculoKpiCreate,
    CalculoKpiRead,
    ConsolidadoPlanesRead,
    ActividadTotalRead,
    DashboardFinancieroRead,
    EstrategiaCreate,
    EstrategiaTotalRead,
    EstrategiaUpdate,
    IndicadorCreate,
    IndicadorUpdate,
    MetricasFinancierasRead,
    PonderacionesTacticasRead,
    PremisasFinancierasRead,
    PlanCreate,
    PlanTotalRead,
    PlanUpdate,
)


def _crear_actividad_modelo(data: ActividadCreate) -> Actividad:
    return Actividad(
        descripcion=data.descripcion,
        responsable=data.responsable,
        tiempo=data.tiempo,
        costo=data.costo,
        tipo_cuenta=data.tipo_cuenta,
    )


def _crear_indicador_modelo(data: IndicadorCreate) -> Indicador:
    return Indicador(
        tipo=data.tipo,
        nombre=data.nombre,
        formula=data.formula,
        frecuencia=data.frecuencia,
        ponderacion=data.ponderacion,
    )


def _crear_estrategia_modelo(data: EstrategiaCreate) -> Estrategia:
    estrategia = Estrategia(
        tipo_estrategia=data.tipo_estrategia,
        descripcion=data.descripcion,
        matriz_id=data.matriz_id,
    )
    for actividad in data.actividades:
        estrategia.actividades.append(_crear_actividad_modelo(actividad))
    for indicador in data.indicadores:
        estrategia.indicadores.append(_crear_indicador_modelo(indicador))
    return estrategia


def crear_plan(db: Session, data: PlanCreate) -> Plan | None:
    if db.get(Empresa, data.empresa_id) is None:
        return None
    plan = Plan(empresa_id=data.empresa_id, tipo=data.tipo)
    for estrategia in data.estrategias:
        plan.estrategias.append(_crear_estrategia_modelo(estrategia))
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def listar_planes(db: Session, empresa_id: int | None = None) -> list[Plan]:
    q = db.query(Plan)
    if empresa_id is not None:
        q = q.filter(Plan.empresa_id == empresa_id)
    return q.all()


def obtener_plan(db: Session, plan_id: int) -> Plan | None:
    return db.get(Plan, plan_id)


def actualizar_plan(db: Session, plan_id: int, data: PlanUpdate) -> Plan | None:
    plan = db.get(Plan, plan_id)
    if plan is None:
        return None
    if data.tipo is not None:
        plan.tipo = data.tipo
    db.commit()
    db.refresh(plan)
    return plan


def eliminar_plan(db: Session, plan_id: int) -> bool:
    plan = db.get(Plan, plan_id)
    if plan is None:
        return False
    db.delete(plan)
    db.commit()
    return True


def crear_estrategia(db: Session, plan_id: int, data: EstrategiaCreate) -> Estrategia | None:
    plan = db.get(Plan, plan_id)
    if plan is None:
        return None
    estrategia = _crear_estrategia_modelo(data)
    plan.estrategias.append(estrategia)
    db.commit()
    db.refresh(estrategia)
    return estrategia


def obtener_estrategia(db: Session, estrategia_id: int) -> Estrategia | None:
    return db.get(Estrategia, estrategia_id)


def actualizar_estrategia(
    db: Session, estrategia_id: int, data: EstrategiaUpdate
) -> Estrategia | None:
    estrategia = db.get(Estrategia, estrategia_id)
    if estrategia is None:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(estrategia, campo, valor)
    db.commit()
    db.refresh(estrategia)
    return estrategia


def eliminar_estrategia(db: Session, estrategia_id: int) -> bool:
    estrategia = db.get(Estrategia, estrategia_id)
    if estrategia is None:
        return False
    db.delete(estrategia)
    db.commit()
    return True


def crear_actividad(
    db: Session, estrategia_id: int, data: ActividadCreate
) -> Actividad | None:
    estrategia = db.get(Estrategia, estrategia_id)
    if estrategia is None:
        return None
    actividad = _crear_actividad_modelo(data)
    estrategia.actividades.append(actividad)
    db.commit()
    db.refresh(actividad)
    return actividad


def obtener_actividad(db: Session, actividad_id: int) -> Actividad | None:
    return db.get(Actividad, actividad_id)


def actualizar_actividad(
    db: Session, actividad_id: int, data: ActividadUpdate
) -> Actividad | None:
    actividad = db.get(Actividad, actividad_id)
    if actividad is None:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(actividad, campo, valor)
    db.commit()
    db.refresh(actividad)
    return actividad


def eliminar_actividad(db: Session, actividad_id: int) -> bool:
    actividad = db.get(Actividad, actividad_id)
    if actividad is None:
        return False
    db.delete(actividad)
    db.commit()
    return True


def crear_indicador(
    db: Session, estrategia_id: int, data: IndicadorCreate
) -> Indicador | None:
    estrategia = db.get(Estrategia, estrategia_id)
    if estrategia is None:
        return None
    indicador = _crear_indicador_modelo(data)
    estrategia.indicadores.append(indicador)
    db.commit()
    db.refresh(indicador)
    return indicador


def listar_indicadores(db: Session, estrategia_id: int) -> list[Indicador] | None:
    estrategia = db.get(Estrategia, estrategia_id)
    if estrategia is None:
        return None
    return list(estrategia.indicadores)


def obtener_indicador(db: Session, indicador_id: int) -> Indicador | None:
    return db.get(Indicador, indicador_id)


def actualizar_indicador(
    db: Session, indicador_id: int, data: IndicadorUpdate
) -> Indicador | None:
    indicador = db.get(Indicador, indicador_id)
    if indicador is None:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(indicador, campo, valor)
    db.commit()
    db.refresh(indicador)
    return indicador


def eliminar_indicador(db: Session, indicador_id: int) -> bool:
    indicador = db.get(Indicador, indicador_id)
    if indicador is None:
        return False
    db.delete(indicador)
    db.commit()
    return True


def validar_ponderaciones_tacticas(
    db: Session, estrategia_id: int
) -> PonderacionesTacticasRead | None:
    estrategia = db.get(Estrategia, estrategia_id)
    if estrategia is None:
        return None
    ponderaciones = [
        indicador.ponderacion or 0.0 for indicador in estrategia.indicadores
    ]
    total = round(sum(ponderaciones), 6)
    return PonderacionesTacticasRead(
        estrategia_id=estrategia_id,
        total_ponderacion=total,
        diferencia=round(1.0 - total, 6),
        valido=kpi_core.validar_ponderaciones(ponderaciones),
        indicadores=list(estrategia.indicadores),
    )


def calcular_indicador(
    db: Session, indicador_id: int, data: CalculoKpiCreate
) -> CalculoKpiRead | None:
    indicador = db.get(Indicador, indicador_id)
    if indicador is None:
        return None
    resultado = kpi_core.calcular_kpi(
        nombre=indicador.nombre,
        numerador=data.numerador,
        denominador=data.denominador,
        formula=indicador.formula or "",
    )
    return CalculoKpiRead(
        indicador_id=indicador.id,
        nombre=resultado.nombre,
        frecuencia=indicador.frecuencia,
        periodo=data.periodo,
        tipo_periodo=data.tipo_periodo,
        numerador=resultado.numerador,
        denominador=resultado.denominador,
        valor=resultado.valor,
        formula=resultado.formula,
    )


def totalizar_plan(db: Session, plan_id: int) -> PlanTotalRead | None:
    plan = db.get(Plan, plan_id)
    if plan is None:
        return None
    return _totalizar_plan_modelo(plan)


def totalizar_consolidado_empresa(
    db: Session, empresa_id: int
) -> ConsolidadoPlanesRead | None:
    if db.get(Empresa, empresa_id) is None:
        return None
    planes = listar_planes(db, empresa_id)
    planes_totalizados = [_totalizar_plan_modelo(plan) for plan in planes]
    total_por_tipo = {plan.tipo: 0.0 for plan in planes}
    for plan in planes_totalizados:
        total_por_tipo[plan.tipo] = round(total_por_tipo.get(plan.tipo, 0.0) + plan.total_costo, 2)

    return ConsolidadoPlanesRead(
        empresa_id=empresa_id,
        total_costo=round(sum(plan.total_costo for plan in planes_totalizados), 2),
        total_por_tipo=total_por_tipo,
        planes=planes_totalizados,
    )


def _totalizar_plan_modelo(plan: Plan) -> PlanTotalRead:
    estrategias = [_totalizar_estrategia_modelo(e) for e in plan.estrategias]
    return PlanTotalRead(
        plan_id=plan.id,
        empresa_id=plan.empresa_id,
        tipo=plan.tipo,
        total_costo=round(sum(e.total_costo for e in estrategias), 2),
        estrategias=estrategias,
    )


def _totalizar_estrategia_modelo(estrategia: Estrategia) -> EstrategiaTotalRead:
    actividades = [
        ActividadTotalRead(
            id=actividad.id,
            descripcion=actividad.descripcion,
            costo=round(actividad.costo or 0.0, 2),
            tipo_cuenta=actividad.tipo_cuenta,
        )
        for actividad in estrategia.actividades
    ]
    return EstrategiaTotalRead(
        id=estrategia.id,
        tipo_estrategia=estrategia.tipo_estrategia,
        descripcion=estrategia.descripcion,
        total_costo=round(sum(a.costo for a in actividades), 2),
        actividades=actividades,
    )


def generar_dashboard_financiero(
    db: Session,
    empresa_id: int,
    ventas_base: float,
    costos_base: float,
    gastos_operativos_base: float | None = None,
    inversion_inicial: float | None = None,
    costos_fijos: float | None = None,
    costos_variables: float | None = None,
) -> DashboardFinancieroRead | None:
    empresa = db.get(Empresa, empresa_id)
    if empresa is None:
        return None

    consolidado = totalizar_consolidado_empresa(db, empresa_id)
    total_planes = consolidado.total_costo
    gastos_base = total_planes if gastos_operativos_base is None else gastos_operativos_base
    inversion = total_planes if inversion_inicial is None else inversion_inicial
    premisas = _obtener_premisas(empresa)

    proyeccion = finanzas.proyectar(
        ventas_0=ventas_base,
        costos_0=costos_base,
        gastos_operativos_0=gastos_base,
        anios=5,
        crecimiento_ventas=premisas.crecimiento_ventas,
        inflacion=premisas.inflacion,
        impuestos=premisas.impuestos,
    )
    flujos = [anio.utilidad_neta for anio in proyeccion.anios]
    punto_equilibrio = _calcular_punto_equilibrio_opcional(
        costos_fijos=costos_fijos,
        costos_variables=costos_variables,
        ventas=ventas_base,
    )

    tir = finanzas.tir(inversion, flujos) if inversion > 0 else None
    return DashboardFinancieroRead(
        empresa_id=empresa_id,
        ventas_base=ventas_base,
        costos_base=costos_base,
        gastos_operativos_base=gastos_base,
        inversion_inicial=inversion,
        total_planes=total_planes,
        premisas=premisas,
        proyeccion=[
            {
                "anio": anio.anio,
                "ventas": anio.ventas,
                "costos": anio.costos,
                "utilidad_bruta": anio.utilidad_bruta,
                "gastos_operativos": anio.gastos_operativos,
                "ebitda": anio.ebitda,
                "utilidad_neta": anio.utilidad_neta,
            }
            for anio in proyeccion.anios
        ],
        flujos=flujos,
        metricas=MetricasFinancierasRead(
            van=finanzas.van(inversion, flujos, wacc=premisas.wacc),
            tir=tir,
            payback=finanzas.payback(inversion, flujos) if inversion > 0 else None,
            punto_equilibrio=punto_equilibrio,
        ),
    )


def _obtener_premisas(empresa: Empresa) -> PremisasFinancierasRead:
    premisas = empresa.premisas
    if premisas is None:
        return PremisasFinancierasRead(
            inflacion=settings.inflacion,
            crecimiento_ventas=settings.crecimiento_ventas,
            impuestos=settings.impuestos,
            wacc=settings.wacc,
        )
    return PremisasFinancierasRead(
        inflacion=premisas.inflacion,
        crecimiento_ventas=premisas.crecimiento_ventas,
        impuestos=premisas.impuestos,
        wacc=premisas.wacc,
    )


def _calcular_punto_equilibrio_opcional(
    costos_fijos: float | None, costos_variables: float | None, ventas: float
) -> float | None:
    if costos_fijos is None or costos_variables is None:
        return None
    try:
        return finanzas.punto_equilibrio(costos_fijos, costos_variables, ventas)
    except ValueError:
        return None
