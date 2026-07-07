# CLAUDE.md — Convenciones del proyecto

Fuente de verdad: `PLAN_DESARROLLO.md`. Leer §9 (Estado actual) antes de cada sesión.

## Reglas
- Código y comentarios de dominio en **español**; nombres en español claro.
- Cálculos NO hardcodeados: viven en `app/core/` como funciones puras + test en `tests/`.
- Validación de pesos/calificaciones en **schema Pydantic**, no en frontend.
- Un endpoint = una responsabilidad. Lógica de negocio en `services/`, no en router.
- El `service` llama al `core` y guarda; nunca mezclar cálculo con acceso a datos.
- Escalas y `sentido` (directo/inverso) como enums/constantes, no strings sueltos.
- Antes de cerrar tarea: `pytest` verde + endpoint probado en `/docs`.
- Commits pequeños por tarea del checklist.

## Comandos
```bash
.venv/Scripts/python.exe -m uvicorn app.main:app --reload   # servidor
.venv/Scripts/python.exe -m pytest                          # tests
```

## Orden por módulo
modelo → schema → servicio → router → template → JS/gráfico.
Construir `core/` (con tests) antes que router y UI.
