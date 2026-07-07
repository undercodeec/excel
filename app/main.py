"""Arranque de FastAPI: monta routers, estáticos y templates."""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routers import matrices

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=settings.app_name)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(matrices.router)


@app.get("/health")
def health():
    """Chequeo de salud del servicio."""
    return {"status": "ok", "app": settings.app_name}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"app_name": settings.app_name})


@app.get("/matrices", response_class=HTMLResponse)
def vista_matrices(request: Request):
    return templates.TemplateResponse(request, "matrices/index.html", {"app_name": settings.app_name})
