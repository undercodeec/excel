"""Arranque de FastAPI: monta routers, estáticos y templates."""
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.routers import auth, cmi, dashboard, empresa, export, matrices, planes, trazabilidad

BASE_DIR = Path(__file__).resolve().parent
STATIC_CSS_PATH = BASE_DIR / "static" / "css" / "estilos.css"
STATIC_JS_DIR = BASE_DIR / "static" / "js"

app = FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.include_router(auth.router)
app.include_router(empresa.router)
app.include_router(matrices.router)
app.include_router(planes.router)
app.include_router(cmi.router)
app.include_router(trazabilidad.router)
app.include_router(dashboard.router)
app.include_router(export.router)


def contexto_base(request: Request) -> dict:
    js_version = max(
        (int(path.stat().st_mtime) for path in STATIC_JS_DIR.glob("*.js")),
        default=0,
    )
    return {
        "app_name": settings.app_name,
        "usuario": request.session.get("username"),
        "empresa_id_sesion": request.session.get("empresa_id"),
        "static_css_version": int(STATIC_CSS_PATH.stat().st_mtime),
        "static_js_version": js_version,
    }


def redirigir_si_no_autenticado(request: Request):
    if request.session.get("usuario_id"):
        return None
    return RedirectResponse(f"/login?next={request.url.path}", status_code=303)


@app.get("/health")
def health():
    """Chequeo de salud del servicio."""
    return {"status": "ok", "app": settings.app_name}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", contexto_base(request))


@app.get("/login", response_class=HTMLResponse)
def vista_login(request: Request, next: str = "/dashboard"):
    if request.session.get("usuario_id"):
        return RedirectResponse(next if next.startswith("/") else "/dashboard", status_code=303)
    contexto = contexto_base(request)
    contexto.update({"error": None, "next_url": next, "username": "", "empresa_id": ""})
    return templates.TemplateResponse(request, "auth/login.html", contexto)


@app.get("/matrices", response_class=HTMLResponse)
def vista_matrices(request: Request):
    redireccion = redirigir_si_no_autenticado(request)
    if redireccion:
        return redireccion
    return templates.TemplateResponse(request, "matrices/index.html", contexto_base(request))


@app.get("/planes", response_class=HTMLResponse)
def vista_planes(request: Request):
    redireccion = redirigir_si_no_autenticado(request)
    if redireccion:
        return redireccion
    return templates.TemplateResponse(request, "planes/index.html", contexto_base(request))


@app.get("/cmi", response_class=HTMLResponse)
def vista_cmi(request: Request):
    redireccion = redirigir_si_no_autenticado(request)
    if redireccion:
        return redireccion
    return templates.TemplateResponse(request, "cmi/index.html", contexto_base(request))


@app.get("/dashboard", response_class=HTMLResponse)
def vista_dashboard(request: Request):
    redireccion = redirigir_si_no_autenticado(request)
    if redireccion:
        return redireccion
    return templates.TemplateResponse(request, "dashboard/index.html", contexto_base(request))
