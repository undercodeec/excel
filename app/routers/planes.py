"""Router CRUD de planes, estrategias y actividades."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.plan import (
    ActividadCreate,
    ActividadRead,
    ActividadUpdate,
    CalculoKpiCreate,
    CalculoKpiRead,
    ConsolidadoPlanesRead,
    DashboardFinancieroRead,
    EstrategiaCreate,
    EstrategiaRead,
    EstrategiaUpdate,
    IndicadorCreate,
    IndicadorRead,
    IndicadorUpdate,
    PonderacionesTacticasRead,
    PlanCreate,
    PlanRead,
    PlanTotalRead,
    PlanUpdate,
)
from app.services import planes as svc

router = APIRouter(prefix="/api/planes", tags=["planes"])


@router.post("", response_model=PlanRead, status_code=201)
def crear(data: PlanCreate, db: Session = Depends(get_db)):
    plan = svc.crear_plan(db, data)
    if plan is None:
        raise HTTPException(404, "Empresa no encontrada")
    return plan


@router.get("", response_model=list[PlanRead])
def listar(empresa_id: int | None = None, db: Session = Depends(get_db)):
    return svc.listar_planes(db, empresa_id)


@router.get("/consolidado/totales", response_model=ConsolidadoPlanesRead)
def totalizar_consolidado(empresa_id: int, db: Session = Depends(get_db)):
    consolidado = svc.totalizar_consolidado_empresa(db, empresa_id)
    if consolidado is None:
        raise HTTPException(404, "Empresa no encontrada")
    return consolidado


@router.get("/dashboard/financiero", response_model=DashboardFinancieroRead)
def dashboard_financiero(
    empresa_id: int,
    ventas_base: float,
    costos_base: float,
    gastos_operativos_base: float | None = None,
    inversion_inicial: float | None = None,
    costos_fijos: float | None = None,
    costos_variables: float | None = None,
    db: Session = Depends(get_db),
):
    dashboard = svc.generar_dashboard_financiero(
        db=db,
        empresa_id=empresa_id,
        ventas_base=ventas_base,
        costos_base=costos_base,
        gastos_operativos_base=gastos_operativos_base,
        inversion_inicial=inversion_inicial,
        costos_fijos=costos_fijos,
        costos_variables=costos_variables,
    )
    if dashboard is None:
        raise HTTPException(404, "Empresa no encontrada")
    return dashboard


@router.get("/{plan_id}", response_model=PlanRead)
def obtener(plan_id: int, db: Session = Depends(get_db)):
    plan = svc.obtener_plan(db, plan_id)
    if plan is None:
        raise HTTPException(404, "Plan no encontrado")
    return plan


@router.patch("/{plan_id}", response_model=PlanRead)
def actualizar(plan_id: int, data: PlanUpdate, db: Session = Depends(get_db)):
    plan = svc.actualizar_plan(db, plan_id, data)
    if plan is None:
        raise HTTPException(404, "Plan no encontrado")
    return plan


@router.delete("/{plan_id}", status_code=204)
def eliminar(plan_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_plan(db, plan_id):
        raise HTTPException(404, "Plan no encontrado")


@router.get("/{plan_id}/totales", response_model=PlanTotalRead)
def totalizar(plan_id: int, db: Session = Depends(get_db)):
    total = svc.totalizar_plan(db, plan_id)
    if total is None:
        raise HTTPException(404, "Plan no encontrado")
    return total


@router.post("/{plan_id}/estrategias", response_model=EstrategiaRead, status_code=201)
def crear_estrategia(
    plan_id: int, data: EstrategiaCreate, db: Session = Depends(get_db)
):
    estrategia = svc.crear_estrategia(db, plan_id, data)
    if estrategia is None:
        raise HTTPException(404, "Plan no encontrado")
    return estrategia


@router.patch("/estrategias/{estrategia_id}", response_model=EstrategiaRead)
def actualizar_estrategia(
    estrategia_id: int, data: EstrategiaUpdate, db: Session = Depends(get_db)
):
    estrategia = svc.actualizar_estrategia(db, estrategia_id, data)
    if estrategia is None:
        raise HTTPException(404, "Estrategia no encontrada")
    return estrategia


@router.delete("/estrategias/{estrategia_id}", status_code=204)
def eliminar_estrategia(estrategia_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_estrategia(db, estrategia_id):
        raise HTTPException(404, "Estrategia no encontrada")


@router.post(
    "/estrategias/{estrategia_id}/actividades",
    response_model=ActividadRead,
    status_code=201,
)
def crear_actividad(
    estrategia_id: int, data: ActividadCreate, db: Session = Depends(get_db)
):
    actividad = svc.crear_actividad(db, estrategia_id, data)
    if actividad is None:
        raise HTTPException(404, "Estrategia no encontrada")
    return actividad


@router.patch("/actividades/{actividad_id}", response_model=ActividadRead)
def actualizar_actividad(
    actividad_id: int, data: ActividadUpdate, db: Session = Depends(get_db)
):
    actividad = svc.actualizar_actividad(db, actividad_id, data)
    if actividad is None:
        raise HTTPException(404, "Actividad no encontrada")
    return actividad


@router.delete("/actividades/{actividad_id}", status_code=204)
def eliminar_actividad(actividad_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_actividad(db, actividad_id):
        raise HTTPException(404, "Actividad no encontrada")


@router.post(
    "/estrategias/{estrategia_id}/indicadores",
    response_model=IndicadorRead,
    status_code=201,
)
def crear_indicador(
    estrategia_id: int, data: IndicadorCreate, db: Session = Depends(get_db)
):
    indicador = svc.crear_indicador(db, estrategia_id, data)
    if indicador is None:
        raise HTTPException(404, "Estrategia no encontrada")
    return indicador


@router.get(
    "/estrategias/{estrategia_id}/indicadores",
    response_model=list[IndicadorRead],
)
def listar_indicadores(estrategia_id: int, db: Session = Depends(get_db)):
    indicadores = svc.listar_indicadores(db, estrategia_id)
    if indicadores is None:
        raise HTTPException(404, "Estrategia no encontrada")
    return indicadores


@router.get(
    "/estrategias/{estrategia_id}/indicadores/ponderaciones",
    response_model=PonderacionesTacticasRead,
)
def validar_ponderaciones_tacticas(
    estrategia_id: int, db: Session = Depends(get_db)
):
    resultado = svc.validar_ponderaciones_tacticas(db, estrategia_id)
    if resultado is None:
        raise HTTPException(404, "Estrategia no encontrada")
    return resultado


@router.get("/indicadores/{indicador_id}", response_model=IndicadorRead)
def obtener_indicador(indicador_id: int, db: Session = Depends(get_db)):
    indicador = svc.obtener_indicador(db, indicador_id)
    if indicador is None:
        raise HTTPException(404, "Indicador no encontrado")
    return indicador


@router.post("/indicadores/{indicador_id}/calcular", response_model=CalculoKpiRead)
def calcular_indicador(
    indicador_id: int, data: CalculoKpiCreate, db: Session = Depends(get_db)
):
    resultado = svc.calcular_indicador(db, indicador_id, data)
    if resultado is None:
        raise HTTPException(404, "Indicador no encontrado")
    return resultado


@router.patch("/indicadores/{indicador_id}", response_model=IndicadorRead)
def actualizar_indicador(
    indicador_id: int, data: IndicadorUpdate, db: Session = Depends(get_db)
):
    indicador = svc.actualizar_indicador(db, indicador_id, data)
    if indicador is None:
        raise HTTPException(404, "Indicador no encontrado")
    return indicador


@router.delete("/indicadores/{indicador_id}", status_code=204)
def eliminar_indicador(indicador_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_indicador(db, indicador_id):
        raise HTTPException(404, "Indicador no encontrado")
