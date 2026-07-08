"""Rutas de autenticacion basica."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.auth import UsuarioSesionRead
from app.services import auth as svc

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def usuario_en_sesion(request: Request, db: Session = Depends(get_db)):
    usuario_id = request.session.get("usuario_id")
    return svc.obtener_usuario_por_id(db, usuario_id)


def contexto_usuario(request: Request, db: Session = Depends(get_db)) -> dict:
    usuario = usuario_en_sesion(request, db)
    return {"usuario": usuario, "autenticado": usuario is not None}


def guardar_sesion(request: Request, usuario) -> None:
    request.session.clear()
    request.session["usuario_id"] = usuario.id
    request.session["empresa_id"] = usuario.empresa_id
    request.session["username"] = usuario.username


@router.post("/login")
def login(
    request: Request,
    empresa_id: int | None = Form(default=None),
    username: str = Form(...),
    password: str = Form(...),
    next_url: str = Form(default="/dashboard"),
    db: Session = Depends(get_db),
):
    usuario = svc.autenticar(db, username=username, password=password, empresa_id=empresa_id)
    if usuario is None:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "app_name": settings.app_name,
                "error": "Usuario, empresa o contrasena invalidos.",
                "next_url": next_url,
                "username": username,
                "empresa_id": empresa_id or "",
            },
            status_code=401,
        )
    guardar_sesion(request, usuario)
    destino = next_url if next_url.startswith("/") and not next_url.startswith("//") else "/dashboard"
    return RedirectResponse(destino, status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/api/auth/me", response_model=UsuarioSesionRead)
def me(usuario=Depends(usuario_en_sesion)):
    if usuario is None:
        raise HTTPException(401, "No autenticado")
    return usuario
