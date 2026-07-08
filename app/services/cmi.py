"""Servicio CMI: CRUD de perspectivas, objetivos, indicadores y mediciones."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core import semaforo
from app.models.cmi import IndicadorCMI, Medicion, ObjetivoCMI, Perspectiva
from app.models.empresa import Empresa
from app.schemas.cmi import (
    IndicadorCMICreate,
    IndicadorCMIUpdate,
    MedicionCreate,
    MedicionUpdate,
    ObjetivoCMICreate,
    ObjetivoCMIUpdate,
    PerspectivaCreate,
    PerspectivaUpdate,
    SemaforoCMIRead,
)


def _crear_medicion_modelo(data: MedicionCreate) -> Medicion:
    return Medicion(
        periodo=data.periodo,
        tipo_periodo=data.tipo_periodo,
        valor=data.valor,
    )


def _crear_indicador_modelo(data: IndicadorCMICreate) -> IndicadorCMI:
    indicador = IndicadorCMI(
        nombre=data.nombre,
        meta=data.meta,
        ponderacion=data.ponderacion,
        rango_min=data.rango_min,
        rango_max=data.rango_max,
        sentido=data.sentido,
        kpi_id=data.kpi_id,
    )
    for medicion in data.mediciones:
        indicador.mediciones.append(_crear_medicion_modelo(medicion))
    return indicador


def _crear_objetivo_modelo(data: ObjetivoCMICreate) -> ObjetivoCMI:
    objetivo = ObjetivoCMI(descripcion=data.descripcion)
    for indicador in data.indicadores:
        objetivo.indicadores.append(_crear_indicador_modelo(indicador))
    return objetivo


def crear_perspectiva(db: Session, data: PerspectivaCreate) -> Perspectiva | None:
    if db.get(Empresa, data.empresa_id) is None:
        return None
    perspectiva = Perspectiva(
        empresa_id=data.empresa_id,
        tipo=data.tipo,
        nombre=data.nombre,
    )
    for objetivo in data.objetivos:
        perspectiva.objetivos.append(_crear_objetivo_modelo(objetivo))
    db.add(perspectiva)
    db.commit()
    db.refresh(perspectiva)
    return perspectiva


def listar_perspectivas(db: Session, empresa_id: int | None = None) -> list[Perspectiva]:
    q = db.query(Perspectiva)
    if empresa_id is not None:
        q = q.filter(Perspectiva.empresa_id == empresa_id)
    return q.all()


def obtener_perspectiva(db: Session, perspectiva_id: int) -> Perspectiva | None:
    return db.get(Perspectiva, perspectiva_id)


def actualizar_perspectiva(
    db: Session, perspectiva_id: int, data: PerspectivaUpdate
) -> Perspectiva | None:
    perspectiva = db.get(Perspectiva, perspectiva_id)
    if perspectiva is None:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(perspectiva, campo, valor)
    db.commit()
    db.refresh(perspectiva)
    return perspectiva


def eliminar_perspectiva(db: Session, perspectiva_id: int) -> bool:
    perspectiva = db.get(Perspectiva, perspectiva_id)
    if perspectiva is None:
        return False
    db.delete(perspectiva)
    db.commit()
    return True


def crear_objetivo(
    db: Session, perspectiva_id: int, data: ObjetivoCMICreate
) -> ObjetivoCMI | None:
    perspectiva = db.get(Perspectiva, perspectiva_id)
    if perspectiva is None:
        return None
    objetivo = _crear_objetivo_modelo(data)
    perspectiva.objetivos.append(objetivo)
    db.commit()
    db.refresh(objetivo)
    return objetivo


def obtener_objetivo(db: Session, objetivo_id: int) -> ObjetivoCMI | None:
    return db.get(ObjetivoCMI, objetivo_id)


def actualizar_objetivo(
    db: Session, objetivo_id: int, data: ObjetivoCMIUpdate
) -> ObjetivoCMI | None:
    objetivo = db.get(ObjetivoCMI, objetivo_id)
    if objetivo is None:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(objetivo, campo, valor)
    db.commit()
    db.refresh(objetivo)
    return objetivo


def eliminar_objetivo(db: Session, objetivo_id: int) -> bool:
    objetivo = db.get(ObjetivoCMI, objetivo_id)
    if objetivo is None:
        return False
    db.delete(objetivo)
    db.commit()
    return True


def crear_indicador(
    db: Session, objetivo_id: int, data: IndicadorCMICreate
) -> IndicadorCMI | None:
    objetivo = db.get(ObjetivoCMI, objetivo_id)
    if objetivo is None:
        return None
    indicador = _crear_indicador_modelo(data)
    objetivo.indicadores.append(indicador)
    db.commit()
    db.refresh(indicador)
    return indicador


def obtener_indicador(db: Session, indicador_id: int) -> IndicadorCMI | None:
    return db.get(IndicadorCMI, indicador_id)


def actualizar_indicador(
    db: Session, indicador_id: int, data: IndicadorCMIUpdate
) -> IndicadorCMI | None:
    indicador = db.get(IndicadorCMI, indicador_id)
    if indicador is None:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(indicador, campo, valor)
    db.commit()
    db.refresh(indicador)
    return indicador


def eliminar_indicador(db: Session, indicador_id: int) -> bool:
    indicador = db.get(IndicadorCMI, indicador_id)
    if indicador is None:
        return False
    db.delete(indicador)
    db.commit()
    return True


def crear_medicion(
    db: Session, indicador_id: int, data: MedicionCreate
) -> Medicion | None:
    indicador = db.get(IndicadorCMI, indicador_id)
    if indicador is None:
        return None
    medicion = _crear_medicion_modelo(data)
    indicador.mediciones.append(medicion)
    db.commit()
    db.refresh(medicion)
    return medicion


def obtener_medicion(db: Session, medicion_id: int) -> Medicion | None:
    return db.get(Medicion, medicion_id)


def actualizar_medicion(
    db: Session, medicion_id: int, data: MedicionUpdate
) -> Medicion | None:
    medicion = db.get(Medicion, medicion_id)
    if medicion is None:
        return None
    cambios = data.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(medicion, campo, valor)
    db.commit()
    db.refresh(medicion)
    return medicion


def eliminar_medicion(db: Session, medicion_id: int) -> bool:
    medicion = db.get(Medicion, medicion_id)
    if medicion is None:
        return False
    db.delete(medicion)
    db.commit()
    return True


def evaluar_medicion(db: Session, medicion_id: int) -> SemaforoCMIRead | None:
    medicion = db.get(Medicion, medicion_id)
    if medicion is None:
        return None
    indicador = medicion.indicador
    resultado = semaforo.evaluar(
        valor_actual=medicion.valor,
        meta=indicador.meta,
        rango_min=indicador.rango_min if indicador.rango_min is not None else indicador.meta,
        rango_max=indicador.rango_max if indicador.rango_max is not None else indicador.meta,
        sentido=semaforo.Sentido(indicador.sentido.value),
    )
    return SemaforoCMIRead(
        indicador_id=indicador.id,
        medicion_id=medicion.id,
        periodo=medicion.periodo,
        valor_actual=resultado.valor_actual,
        meta=resultado.meta,
        cumplimiento=resultado.cumplimiento,
        estado=resultado.estado.value,
        sentido=indicador.sentido,
    )
