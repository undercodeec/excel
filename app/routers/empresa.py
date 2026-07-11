"""Router de Empresa: obtener y actualizar datos de la empresa."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.empresa import Empresa
from app.schemas.empresa import EmpresaRead, EmpresaUpdate

router = APIRouter(prefix="/api/empresa", tags=["empresa"])


@router.get("/{empresa_id}", response_model=EmpresaRead)
def obtener(empresa_id: int, db: Session = Depends(get_db)):
    emp = db.get(Empresa, empresa_id)
    if emp is None:
        raise HTTPException(404, "Empresa no encontrada")
    return emp


@router.patch("/{empresa_id}", response_model=EmpresaRead)
def actualizar(empresa_id: int, data: EmpresaUpdate, db: Session = Depends(get_db)):
    emp = db.get(Empresa, empresa_id)
    if emp is None:
        raise HTTPException(404, "Empresa no encontrada")
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(emp, campo, valor)
    db.commit()
    db.refresh(emp)
    return emp
