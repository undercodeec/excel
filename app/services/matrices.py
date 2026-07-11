"""Servicio de Matrices: orquesta persistencia (models) y cálculo (core)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.empresa import Empresa
from app.models.matriz import Matriz, FactorMatriz
from app.models.enums import TipoMatriz
from app.schemas.matriz import MatrizCreate, MatrizUpdate, ESCALAS
from app.core import ponderacion, holmes, peyea, pestel


# ---------- CRUD ----------
def crear_matriz(db: Session, data: MatrizCreate) -> Matriz:
    matriz = Matriz(empresa_id=data.empresa_id, tipo=data.tipo, nombre=data.nombre)
    for f in data.factores:
        resultado = None
        if f.peso is not None and f.calificacion is not None:
            resultado = round(f.peso * f.calificacion, 6)
        matriz.factores.append(
            FactorMatriz(
                descripcion=f.descripcion,
                peso=f.peso,
                calificacion=f.calificacion,
                resultado=resultado,
                extra_json=f.extra_json,
            )
        )
    db.add(matriz)
    db.commit()
    db.refresh(matriz)
    return matriz


def listar_matrices(db: Session, empresa_id: int | None = None) -> list[Matriz]:
    q = db.query(Matriz)
    if empresa_id is not None:
        q = q.filter(Matriz.empresa_id == empresa_id)
    return q.all()


def obtener_matriz(db: Session, matriz_id: int) -> Matriz | None:
    return db.get(Matriz, matriz_id)


def actualizar_matriz(db: Session, matriz_id: int, data: MatrizUpdate) -> Matriz | None:
    matriz = db.get(Matriz, matriz_id)
    if matriz is None:
        return None
    if data.nombre is not None:
        matriz.nombre = data.nombre
    db.commit()
    db.refresh(matriz)
    return matriz


def eliminar_matriz(db: Session, matriz_id: int) -> bool:
    matriz = db.get(Matriz, matriz_id)
    if matriz is None:
        return False
    db.delete(matriz)
    db.commit()
    return True


# ---------- Cálculo por tipo ----------
def calcular_matriz(db: Session, matriz_id: int) -> dict:
    """Despacha al módulo core según el tipo de matriz y devuelve el resultado."""
    matriz = db.get(Matriz, matriz_id)
    if matriz is None:
        raise ValueError("Matriz no encontrada.")

    empresa = db.get(Empresa, matriz.empresa_id)
    empresa_info = {
        "empresa_nombre": empresa.nombre if empresa else None,
        "empresa_mision": empresa.mision if empresa else None,
        "empresa_vision": empresa.vision if empresa else None,
        "empresa_periodo": empresa.periodo if empresa else None,
        "empresa_moneda": empresa.moneda if empresa else "USD",
    }

    if matriz.tipo == TipoMatriz.peyea:
        return {**empresa_info, **_calcular_peyea(matriz)}
    if matriz.tipo == TipoMatriz.pestel:
        return {**empresa_info, **_calcular_pestel(matriz)}
    if matriz.tipo == TipoMatriz.holmes:
        return {**empresa_info, **_calcular_holmes(matriz)}

    # Tipos ponderados estándar (EFI, EFE, AOOR, MPC, Aprovechabilidad, MADI, MADE)
    escala = ESCALAS.get(matriz.tipo, (1, 4))
    factores = [
        {"descripcion": f.descripcion, "peso": f.peso or 0.0, "calificacion": f.calificacion or 0.0}
        for f in matriz.factores
    ]
    r = ponderacion.calcular(factores, escala_min=escala[0], escala_max=escala[1])
    return {
        **empresa_info,
        "tipo": matriz.tipo.value,
        "total": r.total,
        "pesos_validos": r.pesos_validos,
        "suma_pesos": r.suma_pesos,
        "factores": [
            {"descripcion": x.descripcion, "peso": x.peso, "calificacion": x.calificacion, "resultado": x.resultado}
            for x in r.factores
        ],
    }


def _calcular_peyea(matriz: Matriz) -> dict:
    """extra_json de cada factor: {'dimension': 'FF'|'FI'|'EE'|'VC', ...} con calificacion."""
    dims = {"FF": [], "FI": [], "EE": [], "VC": []}
    for f in matriz.factores:
        dim = (f.extra_json or {}).get("dimension")
        if dim in dims and f.calificacion is not None:
            dims[dim].append(f.calificacion)
    r = peyea.calcular(ff=dims["FF"], fi=dims["FI"], ee=dims["EE"], vc=dims["VC"])
    return {
        "tipo": "peyea",
        "ff": r.ff, "fi": r.fi, "ee": r.ee, "vc": r.vc,
        "x": r.x, "y": r.y, "cuadrante": r.cuadrante,
    }


def _calcular_pestel(matriz: Matriz) -> dict:
    """extra_json: {'categoria', 'tipo': oportunidad|amenaza, 'impacto', 'duracion'}."""
    factores = []
    for f in matriz.factores:
        e = f.extra_json or {}
        factores.append({
            "categoria": e.get("categoria", "Sin categoría"),
            "descripcion": f.descripcion,
            "tipo": e.get("tipo", "oportunidad"),
            "impacto": e.get("impacto", 1),
            "duracion": e.get("duracion", 1),
        })
    r = pestel.calcular(factores)
    return {
        "tipo": "pestel",
        "total_general": r.total_general,
        "totales_categoria": r.totales_categoria,
        "factores": [
            {"categoria": x.categoria, "descripcion": x.descripcion, "puntaje": x.puntaje}
            for x in r.factores
        ],
    }


def _calcular_holmes(matriz: Matriz) -> dict:
    """La matriz pareada se guarda en extra_json del primer factor: {'matriz': [[...]]}."""
    nombres = [f.descripcion for f in matriz.factores]
    matriz_pareada = None
    for f in matriz.factores:
        if f.extra_json and "matriz" in f.extra_json:
            matriz_pareada = f.extra_json["matriz"]
            break
    if matriz_pareada is None:
        raise ValueError("Holmes requiere la matriz pareada en extra_json['matriz'].")
    r = holmes.calcular(nombres, matriz_pareada)
    return {
        "tipo": "holmes",
        "filas": [{"factor": x.factor, "total": x.total, "orden": x.orden} for x in r.filas],
    }
