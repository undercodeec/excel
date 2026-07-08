"""Servicio de autenticacion basica."""
from __future__ import annotations

import hashlib
import hmac
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth import Usuario
from app.models.empresa import Empresa

ITERACIONES = 260_000


def generar_hash_password(password: str) -> str:
    sal = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, ITERACIONES)
    return f"pbkdf2_sha256${ITERACIONES}${sal.hex()}${digest.hex()}"


def verificar_password(password: str, password_hash: str) -> bool:
    try:
        algoritmo, iteraciones, sal_hex, digest_hex = password_hash.split("$", 3)
        if algoritmo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(sal_hex),
            int(iteraciones),
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def obtener_usuario_por_id(db: Session, usuario_id: int | None) -> Usuario | None:
    if usuario_id is None:
        return None
    return db.get(Usuario, usuario_id)


def obtener_usuario_por_username(db: Session, username: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.username == username.strip().lower()))


def crear_usuario(
    db: Session,
    *,
    empresa_id: int,
    username: str,
    password: str,
    nombre: str | None = None,
) -> Usuario:
    usuario = Usuario(
        empresa_id=empresa_id,
        username=username.strip().lower(),
        nombre=nombre,
        password_hash=generar_hash_password(password),
        activo=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def asegurar_usuario_demo_si_no_existe(db: Session, username: str, password: str) -> None:
    hay_usuarios = db.scalar(select(Usuario.id).limit(1))
    if hay_usuarios is not None:
        return
    if username.strip().lower() != "admin" or password != "admin123":
        return

    empresa = db.scalar(select(Empresa).order_by(Empresa.id).limit(1))
    if empresa is None:
        empresa = Empresa(nombre="Empresa demo", periodo="2026", moneda="USD")
        db.add(empresa)
        db.flush()

    db.add(
        Usuario(
            empresa_id=empresa.id,
            username="admin",
            nombre="Administrador",
            password_hash=generar_hash_password("admin123"),
            activo=True,
        )
    )
    db.commit()


def autenticar(db: Session, username: str, password: str, empresa_id: int | None = None) -> Usuario | None:
    asegurar_usuario_demo_si_no_existe(db, username, password)
    usuario = obtener_usuario_por_username(db, username)
    if usuario is None or not usuario.activo:
        return None
    if empresa_id is not None and usuario.empresa_id != empresa_id:
        return None
    if not verificar_password(password, usuario.password_hash):
        return None
    return usuario
