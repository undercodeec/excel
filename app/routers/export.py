"""Router de exportación de entregables (Excel, PDF)."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.export import excel

router = APIRouter(prefix="/api/export", tags=["export"])

_MEDIA_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/excel")
def exportar_excel(empresa_id: int, db: Session = Depends(get_db)):
    """Descarga un libro Excel con todos los entregables de la empresa."""
    buffer = excel.generar_excel_empresa(db, empresa_id)
    if buffer is None:
        raise HTTPException(404, "Empresa no encontrada")
    nombre = f"planificacion_empresa_{empresa_id}.xlsx"
    return StreamingResponse(
        buffer,
        media_type=_MEDIA_XLSX,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
