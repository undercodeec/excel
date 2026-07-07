# Software de Planificación Estratégica — Hacienda Celia María C.A.

Aplicación web que automatiza las matrices estratégicas, los 7 planes y el
Cuadro de Mando Integral (CMI). Backend Python (FastAPI) + frontend HTML/CSS/JS.

## Instalación

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## Ejecución

```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- Salud: http://127.0.0.1:8000/health
- Docs API: http://127.0.0.1:8000/docs

## Tests

```bash
.venv/Scripts/python.exe -m pytest
```

Plan de trabajo completo en `PLAN_DESARROLLO.md`.
