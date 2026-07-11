# Plan de Desarrollo — Software de Planificación Estratégica

> Guía maestra para desarrollar, de forma **organizada y continua**, la aplicación web que
> automatiza las **matrices estratégicas**, los **7 planes** y el **Cuadro de Mando Integral (CMI)**
> de la empresa agroindustrial (Hacienda Celia María C.A.).
>
> **Uso en Claude Code:** este archivo es la fuente de verdad del proyecto. Antes de cada sesión,
> lee la sección "Estado actual del proyecto", elige la siguiente tarea sin marcar `[ ]`, complétala,
> márcala como `[x]` y actualiza el registro de avance. Trabaja fase por fase, sin saltar dependencias.

---

## 1. Objetivo del producto

Reemplazar cuatro libros de Excel por una aplicación web con backend en **Python** y frontend en
**HTML + CSS + JavaScript ligero**, que permita:

1. Capturar los insumos (factores, pesos, calificaciones, actividades, datos periódicos).
2. Calcular automáticamente puntajes, totales, coordenadas, indicadores financieros y semáforos.
3. Visualizar resultados (cuadrantes, radares, dashboards, semáforos).
4. Mantener la **trazabilidad**: Diagnóstico → Estrategias/Planes → KPI → Control (CMI).
5. Exportar entregables a Excel/PDF para conservar el formato actual.

El flujo lógico entre módulos:

```
[1] Diagnóstico        [2] Planes            [3] Indicadores       [4] Control
    17 matrices    →    7 planes tácticos →   Matriz KPI       →    CMI (semáforos)
                        + dashboard fin.
              \______________ Motor de cálculo (backend) ______________/
```

---

## 2. Stack tecnológico (decidido)

| Capa | Elección | Motivo |
|------|----------|--------|
| Lenguaje | Python 3.11+ | Requisito del proyecto |
| Framework web | **FastAPI** | Ligero, tipado, genera docs automáticas (`/docs`) |
| ORM | SQLAlchemy 2.0 | Estándar, relaciones claras |
| Validación | Pydantic v2 | Valida escalas/pesos en la entrada |
| Base de datos | SQLite (dev) → PostgreSQL (prod) | Empezar simple, migrar sin cambiar código |
| Migraciones | Alembic | Control de esquema |
| Frontend | Jinja2 + HTML/CSS + **JS vanilla** | "Algo de JavaScript"; sin framework pesado |
| Gráficos | Chart.js (vía CDN) | Radar, barras, líneas, cuadrantes |
| Finanzas | numpy-financial | VAN (`npv`), TIR (`irr`) |
| Export | openpyxl (Excel), WeasyPrint o reportlab (PDF) | Regenerar entregables |
| Tests | pytest | El motor de cálculo debe tener tests |

> **Regla de arquitectura:** el **motor de cálculo** vive en `app/core/` como **funciones puras**
> (entran datos, salen resultados; sin tocar la base de datos). Así se puede testear de forma aislada
> y se garantiza que los cálculos coinciden con los del Excel original.

---

## 3. Estructura de carpetas objetivo

```
proyecto/
├── app/
│   ├── main.py                 # arranque FastAPI, monta routers y estáticos
│   ├── config.py               # settings (DB URL, premisas por defecto)
│   ├── database.py             # engine, session, Base
│   ├── models/                 # SQLAlchemy (tablas)
│   │   ├── empresa.py
│   │   ├── matriz.py
│   │   ├── plan.py
│   │   ├── kpi.py
│   │   └── cmi.py
│   ├── schemas/                # Pydantic (entrada/salida + validaciones)
│   ├── core/                   # MOTOR DE CÁLCULO (funciones puras, con tests)
│   │   ├── ponderacion.py      # peso × calificación, totales, validación de pesos
│   │   ├── holmes.py           # comparación pareada, orden
│   │   ├── peyea.py            # coordenadas X/Y, cuadrante
│   │   ├── pestel.py           # impacto × duración × signo
│   │   ├── finanzas.py         # proyección 5 años, VAN, TIR, payback, punto equilibrio
│   │   ├── kpi.py              # numerador/denominador, ponderación táctica
│   │   └── semaforo.py         # evaluación de rangos de alerta CMI
│   ├── routers/                # endpoints por módulo
│   │   ├── matrices.py
│   │   ├── planes.py
│   │   ├── kpis.py
│   │   └── cmi.py
│   ├── services/               # orquesta modelos + core (lógica de negocio)
│   ├── export/                 # generación de Excel y PDF
│   ├── templates/              # Jinja2 (una carpeta por módulo)
│   └── static/
│       ├── css/
│       └── js/                 # fetch a la API + Chart.js
├── tests/                      # pytest, refleja app/core/
├── alembic/                    # migraciones
├── requirements.txt
├── CLAUDE.md                   # convenciones cortas para Claude Code (ver §8)
├── PLAN_DESARROLLO.md          # este archivo
└── README.md
```

---

## 4. Modelo de datos (referencia)

Relaciones principales (una `Empresa` es la raíz de todo):

- **Empresa** (nombre, misión, visión, periodo, moneda) `1—N` todo lo demás.
- **Matriz** (tipo, nombre) `1—N` **FactorMatriz** (descripción, peso, calificación, resultado, extra_json).
  - `tipo` ∈ {holmes, foda_cuali, foda_cuanti, efi, efe, cadena_valor, aoor, aprovechabilidad,
    cinco_fuerzas, mpc, ansoff, pestel, peyea, madi, made}.
  - `extra_json` guarda campos específicos por tipo (p. ej. coordenadas PEYEA, matriz pareada Holmes).
- **Plan** (tipo) `1—N` **Estrategia** `1—N` **Actividad** (descripción, responsable, tiempo, costo, tipo_cuenta).
  - `tipo` ∈ {financiero, marketing, operaciones, mejoras, tecnologico, compras, control}.
- **PremisasFinancieras** (inflación, crecimiento_ventas, impuestos, wacc) `N—1` Empresa.
- **Estrategia** `1—N` **Indicador** (KPI) (tipo, nombre, formula, frecuencia, ponderacion).
- **Perspectiva** (financiera/clientes/procesos/aprendizaje) `1—N` **ObjetivoCMI** `1—N`
  **IndicadorCMI** (nombre, meta, ponderacion, rango_min, rango_max) `1—N` **Medicion** (periodo, valor).

> **Nota de flexibilidad:** el modelo de `Medicion` debe soportar frecuencias distintas
> (mensual, trimestral, semestral, anual, por ciclo de cosecha). Usar un campo `periodo` string
> + `tipo_periodo` enum, no columnas fijas por mes.

---

## 5. Lógica de cálculo a implementar (núcleo del sistema)

Estos son los cálculos extraídos de los Excel. Cada uno debe ir en `app/core/` con su test en `tests/`.

### 5.1 Ponderación estándar (`ponderacion.py`)
Aplica a EFI, EFE, AOOR, MPC, Aprovechabilidad, MADI, MADE.
```
resultado_i = peso_i * calificacion_i
total       = Σ resultado_i
```
- Validación: `Σ peso_i == 1.0` (con tolerancia ±0.01).
- Escalas fijas: calificación ∈ {1,2,3,4} (EFI/EFE/MADI) o {1..5} (aprovechabilidad/MPC).
- Diagnóstico MADI: calificación 4=Fortaleza mayor, 3=menor, 2=Debilidad menor, 1=mayor.

### 5.2 Matriz Holmes (`holmes.py`)
Comparación pareada de N factores.
```
celda(i,j) ∈ {0, 0.5, 1}   (i vs j; diagonal vacía)
total_i    = Σ_j celda(i,j)
orden      = ranking descendente por total_i
```

### 5.3 PEYEA (`peyea.py`)
Cuatro dimensiones con puntaje ponderado (peso × calificación):
- FF (Fuerza Financiera): calificaciones positivas → promedio ponderado ≥ 0.
- FI (Fuerza de la Industria): positivas.
- EE (Estabilidad del Entorno): calificaciones negativas (−1..−5).
- VC (Ventaja Competitiva): negativas.
```
Eje X = FI + VC
Eje Y = FF + EE
Cuadrante:  X>0,Y>0 = Agresivo | X<0,Y>0 = Conservador
            X<0,Y<0 = Defensivo | X>0,Y<0 = Competitivo
```
Devolver también las coordenadas para graficar el vector.

### 5.4 PESTEL (`pestel.py`)
```
signo        = +1 si OPORTUNIDAD, -1 si AMENAZA
puntaje_ind  = impacto * duracion * signo      (impacto y duración en 1..4)
total_factor = Σ puntaje_ind por categoría (Político, Económico, ...)
```

### 5.5 Finanzas (`finanzas.py`)
Premisas por defecto: inflación 4%, crecimiento_ventas 8%, impuestos 36%, WACC 12%.
Proyección compuesta a 5 años:
```
Ventas_n        = Ventas_(n-1) * (1 + crecimiento_ventas)
Costos_n        = Costos_(n-1) * (1 + inflación)
Utilidad bruta  = Ventas − Costos
EBITDA          = Utilidad bruta − Gastos operativos
Utilidad neta   = EBITDA * (1 − impuestos)
```
Métricas de evaluación:
- **VAN**: `numpy_financial.npv(wacc, flujos)` con inversión inicial negativa.
- **TIR**: `numpy_financial.irr(flujos)`.
- **Payback**: primer año donde el flujo acumulado ≥ inversión (interpolar meses).
- **Punto de equilibrio** = Costos fijos / (1 − Costos variables/Ventas).

### 5.6 KPI (`kpi.py`)
```
valor_kpi = numerador / denominador     (evitar división por cero → devolver None/0)
```
- Cada indicador tiene una `ponderacion` táctica; validar que el conjunto sume ~1.0.
- Guardar la fórmula como texto legible ("(Mercados identificados / Mercados analizados)").

### 5.7 Semáforos CMI (`semaforo.py`)
Cada indicador tiene `meta`, `rango_min`, `rango_max` y `valor_actual`.
```
cumplimiento = valor_actual / meta
estado:
  VERDE    si valor_actual cumple o supera la meta
  AMARILLO si cae dentro del rango de alerta
  ROJO     si está por debajo del umbral inferior
```
> Ojo: algunos indicadores son "inversos" (menor es mejor, p. ej. "# de quejas", "% de NC").
> Incluir un flag `sentido` ∈ {directo, inverso} para invertir la comparación.

---

## 6. Roadmap por fases (checklist continuo)

Marca `[x]` al completar. No inicies una fase sin cerrar la anterior. Cada fase tiene su
**Definición de Hecho (DoD)**.

### Fase 0 — Setup del proyecto
- [x] Crear estructura de carpetas de §3
- [x] `requirements.txt` con dependencias de §2
- [x] Entorno virtual + instalación
- [x] `app/main.py` con FastAPI mínimo (endpoint `/health`)
- [x] `app/database.py` (engine SQLite, session, Base)
- [x] `config.py` con premisas financieras por defecto
- [x] Inicializar Git + `.gitignore`
- **DoD:** `uvicorn app.main:app --reload` levanta y `/health` responde 200; `/docs` visible.

### Fase 1 — Modelo de datos + motor de cálculo
- [x] Modelos SQLAlchemy de §4 (Empresa, Matriz, Plan, KPI, CMI)
- [x] Configurar Alembic + primera migración
- [x] `core/ponderacion.py` + tests
- [x] `core/holmes.py` + tests
- [x] `core/peyea.py` + tests
- [x] `core/pestel.py` + tests
- [x] `core/finanzas.py` + tests (validar VAN/TIR contra valores del Excel: VAN≈411.622, TIR≈28.4%) — funciones OK; test de control Excel `skip` hasta tener datos reales
- [x] `core/kpi.py` + tests
- [x] `core/semaforo.py` + tests (incluir caso inverso)
- **DoD:** `pytest` pasa en verde; los cálculos coinciden con los del Excel original.

### Fase 2 — Módulo Matrices
- [x] Schemas Pydantic con validación de pesos (suma=1) y escalas
- [x] Router CRUD de matrices y factores
- [x] Endpoint de cálculo por tipo de matriz
- [x] UI: listado de matrices + formulario/tabla editable
- [x] Visualización PEYEA (gráfico de cuadrantes con el vector)
- [x] Visualización Ansoff (cuadrícula 2×2)
- [x] Visualización 5 Fuerzas (radar) y MPC (barras comparativas)
- **DoD:** se puede crear una matriz, capturar datos y ver el resultado calculado + su gráfico.

### Fase 3 — Módulo Planes
- [x] CRUD de planes → estrategias → actividades
- [x] Totalización automática por plan y consolidado
- [x] Endpoint de dashboard financiero (proyección 5 años)
- [x] UI: tablas editables por plan (7 pestañas)
- [x] UI: dashboard financiero (estado de resultados, flujo, balance, VAN/TIR/payback)
- **DoD:** cambiar una premisa recalcula todo el dashboard; los 7 planes suman su TOTAL.

### Fase 4 — Módulo KPI
- [x] CRUD estrategia → actividad → indicador
- [x] Gestión de ponderaciones tácticas + validación de suma
- [x] Cálculo de KPI (numerador/denominador) por frecuencia
- [x] UI: matriz de indicadores con edición inline
- **DoD:** cada actividad tiene su KPI con fórmula y frecuencia; los pesos suman ~100%.

### Fase 5 — Módulo CMI (Cuadro de Mando Integral)
- [x] CRUD perspectivas → objetivos → indicadores → mediciones
- [x] Captura periódica de valores (soportar varias frecuencias)
- [x] Evaluación de semáforos (directo/inverso)
- [x] UI: tablero por 4 perspectivas con estado semaforizado
- [x] Gráficos por perspectiva (líneas de tendencia, cumplimiento)
- **DoD:** al ingresar un valor, el indicador se pinta verde/amarillo/rojo automáticamente.

### Fase 6 — Integración, trazabilidad y exportación
- [x] Vincular Estrategia (matrices) → Plan → KPI → Indicador CMI
- [x] Dashboard general (resumen de los 4 módulos)
- [x] Exportar a Excel (openpyxl) conservando estructura de los entregables
- [~] Exportar a PDF (informe ejecutivo) — **omitido por decisión del usuario (no se requiere PDF)**
- **DoD:** desde una estrategia se navega a su plan, su KPI y su indicador de control. (endpoint de trazabilidad)

### Fase 7 — Pulido y despliegue
- [x] Manejo de errores y mensajes de validación en UI
- [x] Autenticación básica (login por empresa/usuario)
- [x] README con instrucciones de instalación y uso
- [x] Despliegue (Docker opcional)
- [ ] Migrar a PostgreSQL (probar la misma migración Alembic) — **dejar al final por decisión del usuario**
- **DoD:** un usuario nuevo puede instalar, cargar datos y exportar un informe completo.

---

## 7. Orden de trabajo recomendado (para no bloquearse)

1. Construye **siempre** `core/` (con tests) antes que su router y su UI.
2. Dentro de cada módulo: **modelo → schema → servicio → router → template → JS/gráfico**.
3. Prueba cada endpoint en `/docs` antes de escribir el frontend que lo consume.
4. No mezcles cálculo con acceso a datos: el `service` llama al `core` y guarda el resultado.

---

## 8. Convenciones (copiar lo esencial a `CLAUDE.md`)

- Código y comentarios de dominio en **español**; nombres de variables/funciones en español claro.
- Los cálculos NO se hardcodean: viven en `app/core/` como funciones puras y tienen test.
- Toda entrada de pesos/calificaciones se valida en el **schema Pydantic**, no en el frontend.
- Un endpoint = una responsabilidad. La lógica de negocio va en `services/`, no en el router.
- Escalas fijas y "sentido" (directo/inverso) se definen como enums/constantes, nunca strings sueltos.
- Antes de cerrar una tarea: `pytest` en verde y el endpoint probado en `/docs`.
- Commits pequeños y descriptivos por tarea del checklist.

---

## 9. Estado actual del proyecto

> Actualiza esta sección al final de cada sesión de Claude Code.

- **Fase actual:** Fase 7 — Pulido y despliegue (en curso)
- **Última tarea completada:** Fase 7: despliegue Docker opcional — `Dockerfile`, `.dockerignore`, `docker-compose.yml` con volumen persistente SQLite, `SECRET_KEY` por entorno y arranque con `alembic upgrade head` + `uvicorn`; README actualizado; 72 tests verdes + 1 skip
- **Siguiente tarea:** Migrar a PostgreSQL (probar la misma migración Alembic) — al final por decisión del usuario
- **Bloqueos / notas:** PostgreSQL queda al final por decisión del usuario y no se puede probar aún en esta máquina porque `psql`/`postgres` no están instalados. Docker tampoco está instalado localmente, por lo que el build queda pendiente de validar en un entorno con Docker. Falta router de Empresa (matrices requieren empresa_id existente; en tests se inserta directo). Ansoff/5F/MPC tienen gráfico pero sin captura de datos específica aún. SRI del CDN Chart.js pendiente (Fase 7). `test_valores_control_excel` sigue en `skip`. Trabajo de Fases 3-5 aún sin commitear (git log solo llega a Fase 2). La vinculación es de backend/datos; UI de navegación de trazabilidad puede sumarse junto al dashboard general.

### Registro de avance
| Fecha | Sesión | Qué se hizo | Siguiente paso |
|-------|--------|-------------|----------------|
| 2026-07-07 | 1 | Fase 0: estructura §3, requirements, venv+install, config, database, main+/health (200), git init | Fase 1: modelos SQLAlchemy |
| 2026-07-07 | 1 | Fase 1: 12 modelos SQLAlchemy §4, Alembic init+migración `7c3f6280e8d5` (upgrade head), core {ponderacion,holmes,peyea,pestel,finanzas,kpi,semaforo}, 32 tests verdes | Fase 2: schemas + router Matrices |
| 2026-07-07 | 1 | Fase 2: schema matriz (valida pesos/escalas), service (CRUD+cálculo por tipo), router `/api/matrices`, UI (base/index/matrices + estilos.css + matrices.js con Chart.js: PEYEA/radar/barras/Ansoff), conftest StaticPool, 36 tests verdes | Fase 3: CRUD Planes |
| 2026-07-07 | 1 | Fase 3: CRUD de planes/estrategias/actividades con schemas, service, router `/api/planes` y tests de integración; 40 tests verdes + 1 skip | Fase 3: totalización automática por plan y consolidado |
| 2026-07-07 | 1 | Fase 3: totalización automática por plan, por estrategia y consolidado por empresa; endpoints `/api/planes/{plan_id}/totales` y `/api/planes/consolidado/totales`; 42 tests verdes + 1 skip | Fase 3: endpoint de dashboard financiero |
| 2026-07-07 | 1 | Fase 3: endpoint `/api/planes/dashboard/financiero` con proyección a 5 años, premisas por empresa o default, VAN, TIR, payback y punto de equilibrio; 45 tests verdes + 1 skip | Fase 3: UI tablas editables por plan |
| 2026-07-07 | 1 | Fase 3: UI `/planes` con 7 pestañas, creación de planes, alta/edición/borrado de estrategias y actividades, totales por plan/empresa; 47 tests verdes + 1 skip; servidor verificado en 127.0.0.1:8000 | Fase 3: UI dashboard financiero |
| 2026-07-07 | 1 | Fase 3: UI dashboard financiero en `/planes` con parámetros base, valores demo, premisas, métricas VAN/TIR/payback/punto equilibrio, tabla de proyección y gráfico Chart.js; 47 tests verdes + 1 skip; `/planes` 200 | Fase 4: CRUD KPI |
| 2026-07-07 | 1 | Fase 4: schemas, service y router para indicadores KPI por estrategia; endpoints CRUD `/api/planes/estrategias/{estrategia_id}/indicadores` y `/api/planes/indicadores/{indicador_id}`; estrategias devuelven actividades e indicadores; 51 tests verdes + 1 skip | Fase 4: ponderaciones tácticas |
| 2026-07-07 | 1 | Fase 4: endpoint de validación de ponderaciones tácticas por estrategia usando `app.core.kpi.validar_ponderaciones`; devuelve total, diferencia, estado válido e indicadores; 53 tests verdes + 1 skip | Fase 4: cálculo KPI por frecuencia |
| 2026-07-07 | 1 | Fase 4: endpoint `/api/planes/indicadores/{indicador_id}/calcular` para numerador/denominador por periodo y tipo_periodo, usando fórmula/frecuencia del indicador; 55 tests verdes + 1 skip | Fase 4: UI matriz de indicadores |
| 2026-07-07 | 1 | Fase 4: UI en `/planes` para matriz de indicadores con alta/edición/borrado inline, validación de ponderaciones por estrategia y cálculo rápido de KPI; 55 tests verdes + 1 skip; `/planes` 200 | Fase 5: CRUD CMI |
| 2026-07-07 | 1 | Fase 5: schemas, service y router `/api/cmi` para perspectivas, objetivos, indicadores y mediciones; captura flexible por `periodo`/`tipo_periodo`; endpoint `/api/cmi/mediciones/{medicion_id}/semaforo`; 59 tests verdes + 1 skip | Fase 5: UI tablero CMI |
| 2026-07-07 | 1 | Fase 5: vista `/cmi` con tablero por cuatro perspectivas, creación rápida de perspectivas/objetivos/indicadores, captura de mediciones, evaluación semaforizada y gráficos de tendencia por perspectiva; 60 tests verdes + 1 skip; servidor verificado en 127.0.0.1:8001 | Fase 6: trazabilidad |
| 2026-07-07 | 1 | Fase 6: trazabilidad — FKs `Estrategia.matriz_id` e `IndicadorCMI.kpi_id`, migración Alembic `a1b2c3d4e5f6` (up/down OK), schemas/services propagan los enlaces, módulo `trazabilidad` (schema+service+router) con `GET /api/trazabilidad/estrategia/{id}`; 63 tests verdes + 1 skip; ruta visible en OpenAPI | Fase 6: dashboard general (resumen 4 módulos) |
| 2026-07-07 | 1 | Fase 6: dashboard general — módulo `dashboard` (schema+service+router) `GET /api/dashboard/general` que agrega Matrices/Planes/KPI/CMI + semáforos por última medición + trazabilidad; vista `/dashboard` (tarjetas + doughnut Chart.js), nav e índice actualizados; 67 tests verdes + 1 skip; `/dashboard` 200 en vivo (puerto 8009) | Fase 6: exportar a Excel (openpyxl) |
| 2026-07-07 | 1 | Fase 6: exportación Excel — `app/export/excel.py` (hojas Resumen/Matrices/Planes/KPI/CMI, estilos, TOTAL, semáforo coloreado) y router `GET /api/export/excel`; enlace de descarga en `/dashboard`; 70 tests verdes + 1 skip | Fase 6: exportar a PDF (reportlab) |
| 2026-07-08 | 1 | Fase 7: manejo de errores y validación UI — helper compartido para errores API/422, toasts accesibles, marcado de campos inválidos y manejo explícito de acciones async en Matrices/Planes/CMI/Dashboard; 70 tests verdes + 1 skip; JS validado con `node --check` del runtime local | Fase 7: autenticación básica |
| 2026-07-08 | 1 | Fase 7: autenticación básica — tabla `usuario`, servicio de auth con PBKDF2, login/logout con sesión firmada, protección de vistas `/matrices`, `/planes`, `/cmi`, `/dashboard`, usuario demo local y tests de flujo; migración `b2c3d4e5f6a7` aplicada; 72 tests verdes + 1 skip | Fase 7: migrar a PostgreSQL |
| 2026-07-08 | 1 | Fase 7: README — guía completa de instalación, `alembic upgrade head`, ejecución con uvicorn, login demo, variables `.env`, flujo por módulos, exportación Excel, tests, migraciones y notas operativas; PostgreSQL movido al final por decisión del usuario | Fase 7: despliegue (Docker opcional) |
| 2026-07-08 | 1 | Fase 7: despliegue Docker opcional — `Dockerfile`, `.dockerignore`, `docker-compose.yml` con SQLite persistente en volumen, `SECRET_KEY` por entorno y comando de arranque con migraciones Alembic + Uvicorn; README actualizado; Docker no instalado localmente para build | Fase 7: PostgreSQL al final |

---

## 10. Referencia rápida del dominio

**17 matrices:** Holmes, FODA cualitativo, FODA cuantitativo, EFI, EFE, Cadena de Valor, AOOR,
Aprovechabilidad (+ índices), Calificación de Variables / 5 Fuerzas, Perfil Competitivo (MPC),
Ansoff, PESTEL, PEYEA, MADI, MADE.

**7 planes** (columnas: Tipo de estrategia | Estrategia | Actividad | Responsable | Tiempo | Costo | Tipo de cuenta):
Financiero, Marketing, Operaciones, Mejoras, Tecnológico/Sistemas, Compras, Control.

**4 perspectivas CMI:** Financiera, Clientes, Procesos Internos, Aprendizaje y Crecimiento.

**Premisas financieras por defecto:** inflación 4% · crecimiento de ventas 8% · impuestos 36% · WACC 12%.

**Valores de control** (para validar el motor financiero): VAN ≈ 411.622 · TIR ≈ 28.4% ·
Payback ≈ 2 años 4 meses.
