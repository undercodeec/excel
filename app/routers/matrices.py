"""Router CRUD de matrices + endpoint de cálculo."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.matriz import MatrizCreate, MatrizRead, MatrizUpdate
from app.schemas.trazabilidad import InformeMatrizRead
from app.services import matrices as svc
from app.services import trazabilidad as svc_traza

router = APIRouter(prefix="/api/matrices", tags=["matrices"])


@router.post("", response_model=MatrizRead, status_code=201)
def crear(data: MatrizCreate, db: Session = Depends(get_db)):
    return svc.crear_matriz(db, data)


@router.get("", response_model=list[MatrizRead])
def listar(empresa_id: int | None = None, db: Session = Depends(get_db)):
    return svc.listar_matrices(db, empresa_id)


@router.get("/{matriz_id}", response_model=MatrizRead)
def obtener(matriz_id: int, db: Session = Depends(get_db)):
    m = svc.obtener_matriz(db, matriz_id)
    if m is None:
        raise HTTPException(404, "Matriz no encontrada")
    return m


@router.patch("/{matriz_id}", response_model=MatrizRead)
def actualizar(matriz_id: int, data: MatrizUpdate, db: Session = Depends(get_db)):
    m = svc.actualizar_matriz(db, matriz_id, data)
    if m is None:
        raise HTTPException(404, "Matriz no encontrada")
    return m


@router.delete("/{matriz_id}", status_code=204)
def eliminar(matriz_id: int, db: Session = Depends(get_db)):
    if not svc.eliminar_matriz(db, matriz_id):
        raise HTTPException(404, "Matriz no encontrada")


@router.get("/{matriz_id}/calculo")
def calcular(matriz_id: int, db: Session = Depends(get_db)):
    try:
        return svc.calcular_matriz(db, matriz_id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{matriz_id}/informe", response_model=InformeMatrizRead)
def informe(matriz_id: int, db: Session = Depends(get_db)):
    """Informe completo: empresa + cálculo + estrategias/planes vinculados desde CMI."""
    resultado = svc_traza.trazar_matriz(db, matriz_id)
    if resultado is None:
        raise HTTPException(404, "Matriz no encontrada")
    return resultado
