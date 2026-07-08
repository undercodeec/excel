"""Router CRUD del Cuadro de Mando Integral."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.cmi import (
    IndicadorCMICreate,
    IndicadorCMIRead,
    IndicadorCMIUpdate,
    MedicionCreate,
    MedicionRead,
    MedicionUpdate,
    ObjetivoCMICreate,
    ObjetivoCMIRead,
    ObjetivoCMIUpdate,
    PerspectivaCreate,
    PerspectivaRead,
    PerspectivaUpdate,
    SemaforoCMIRead,
)
from app.services import cmi as svc

router = APIRouter(prefix="/api/cmi", tags=["cmi"])


@router.post("/perspectivas", response_model=PerspectivaRead, status_code=201)
def crear_perspectiva(data: PerspectivaCreate, db: Session = Depends(get_db)):
    perspectiva = svc.crear_perspectiva(db, data)
    if perspectiva is None:
        raise HTTPException(404, "Empresa no encontrada")
    return perspectiva


@router.get("/perspectivas", response_model=list[PerspectivaRead])
def listar_perspectivas(
    empresa_id: int | None = None, db: Session = Depends(get_db)
):
    return svc.listar_perspectivas(db, empresa_id)


@router.get("/perspectivas/{perspectiva_id}", response_model=PerspectivaRead)
def obtener_perspectiva(perspectiva_id: int, db: Session = Depends(get_db)):
    perspectiva = svc.obtener_perspectiva(db, perspectiva_id)
    if perspectiva is None:
        raise HTTPException(404, "Perspectiva no encontrada")
    return perspectiva


@router.patch("/perspectivas/{perspectiva_id}", response_model=PerspectivaRead)
def actualizar_perspectiva(
    perspectiva_id: int, data: PerspectivaUpdate, db: Session = Depends(get_db)
):
    perspectiva = svc.actualizar_perspectiva(db, perspectiva_id, data)
    if perspectiva is None:
        raise HTTPException(404, "Perspectiva no encontrada")
    return perspectiva


@router.delete("/perspectivas/{perspectiva_id}", status_code=204)
def eliminar_perspectiva(perspectiva_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_perspectiva(db, perspectiva_id):
        raise HTTPException(404, "Perspectiva no encontrada")


@router.post(
    "/perspectivas/{perspectiva_id}/objetivos",
    response_model=ObjetivoCMIRead,
    status_code=201,
)
def crear_objetivo(
    perspectiva_id: int, data: ObjetivoCMICreate, db: Session = Depends(get_db)
):
    objetivo = svc.crear_objetivo(db, perspectiva_id, data)
    if objetivo is None:
        raise HTTPException(404, "Perspectiva no encontrada")
    return objetivo


@router.patch("/objetivos/{objetivo_id}", response_model=ObjetivoCMIRead)
def actualizar_objetivo(
    objetivo_id: int, data: ObjetivoCMIUpdate, db: Session = Depends(get_db)
):
    objetivo = svc.actualizar_objetivo(db, objetivo_id, data)
    if objetivo is None:
        raise HTTPException(404, "Objetivo no encontrado")
    return objetivo


@router.delete("/objetivos/{objetivo_id}", status_code=204)
def eliminar_objetivo(objetivo_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_objetivo(db, objetivo_id):
        raise HTTPException(404, "Objetivo no encontrado")


@router.post(
    "/objetivos/{objetivo_id}/indicadores",
    response_model=IndicadorCMIRead,
    status_code=201,
)
def crear_indicador(
    objetivo_id: int, data: IndicadorCMICreate, db: Session = Depends(get_db)
):
    indicador = svc.crear_indicador(db, objetivo_id, data)
    if indicador is None:
        raise HTTPException(404, "Objetivo no encontrado")
    return indicador


@router.patch("/indicadores/{indicador_id}", response_model=IndicadorCMIRead)
def actualizar_indicador(
    indicador_id: int, data: IndicadorCMIUpdate, db: Session = Depends(get_db)
):
    indicador = svc.actualizar_indicador(db, indicador_id, data)
    if indicador is None:
        raise HTTPException(404, "Indicador no encontrado")
    return indicador


@router.delete("/indicadores/{indicador_id}", status_code=204)
def eliminar_indicador(indicador_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_indicador(db, indicador_id):
        raise HTTPException(404, "Indicador no encontrado")


@router.post(
    "/indicadores/{indicador_id}/mediciones",
    response_model=MedicionRead,
    status_code=201,
)
def crear_medicion(
    indicador_id: int, data: MedicionCreate, db: Session = Depends(get_db)
):
    medicion = svc.crear_medicion(db, indicador_id, data)
    if medicion is None:
        raise HTTPException(404, "Indicador no encontrado")
    return medicion


@router.patch("/mediciones/{medicion_id}", response_model=MedicionRead)
def actualizar_medicion(
    medicion_id: int, data: MedicionUpdate, db: Session = Depends(get_db)
):
    medicion = svc.actualizar_medicion(db, medicion_id, data)
    if medicion is None:
        raise HTTPException(404, "Medicion no encontrada")
    return medicion


@router.get("/mediciones/{medicion_id}/semaforo", response_model=SemaforoCMIRead)
def evaluar_medicion(medicion_id: int, db: Session = Depends(get_db)):
    resultado = svc.evaluar_medicion(db, medicion_id)
    if resultado is None:
        raise HTTPException(404, "Medicion no encontrada")
    return resultado


@router.delete("/mediciones/{medicion_id}", status_code=204)
def eliminar_medicion(medicion_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_medicion(db, medicion_id):
        raise HTTPException(404, "Medicion no encontrada")
