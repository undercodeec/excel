"""Router de trazabilidad: navegación Estrategia → Plan → KPI → Indicador CMI."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.trazabilidad import TrazabilidadEstrategiaRead
from app.services import trazabilidad as svc

router = APIRouter(prefix="/api/trazabilidad", tags=["trazabilidad"])


@router.get("/estrategia/{estrategia_id}", response_model=TrazabilidadEstrategiaRead)
def trazar_estrategia(estrategia_id: int, db: Session = Depends(get_db)):
    """Reconstruye la cadena de trazabilidad de una estrategia."""
    resultado = svc.trazar_estrategia(db, estrategia_id)
    if resultado is None:
        raise HTTPException(404, "Estrategia no encontrada")
    return resultado
