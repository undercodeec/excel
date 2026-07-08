"""Router del dashboard general: resumen consolidado de los 4 módulos."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import DashboardGeneralRead
from app.services import dashboard as svc

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/general", response_model=DashboardGeneralRead)
def dashboard_general(empresa_id: int, db: Session = Depends(get_db)):
    """Resumen agregado de Matrices, Planes, KPI y CMI para una empresa."""
    resultado = svc.generar_dashboard_general(db, empresa_id)
    if resultado is None:
        raise HTTPException(404, "Empresa no encontrada")
    return resultado
