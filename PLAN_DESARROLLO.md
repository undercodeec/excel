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
- [ ] Schemas Pydantic con validación de pesos (suma=1) y escalas
- [ ] Router CRUD de matrices y factores
- [ ] Endpoint de cálculo por tipo de matriz
- [ ] UI: listado de matrices + formulario/tabla editable
- [ ] Visualización PEYEA (gráfico de cuadrantes con el vector)
- [ ] Visualización Ansoff (cuadrícula 2×2)
- [ ] Visualización 5 Fuerzas (radar) y MPC (barras comparativas)
- **DoD:** se puede crear una matriz, capturar datos y ver el resultado calculado + su gráfico.

### Fase 3 — Módulo Planes
- [ ] CRUD de planes → estrategias → actividades
- [ ] Totalización automática por plan y consolidado
- [ ] Endpoint de dashboard financiero (proyección 5 años)
- [ ] UI: tablas editables por plan (7 pestañas)
- [ ] UI: dashboard financiero (estado de resultados, flujo, balance, VAN/TIR/payback)
- **DoD:** cambiar una premisa recalcula todo el dashboard; los 7 planes suman su TOTAL.

### Fase 4 — Módulo KPI
- [ ] CRUD estrategia → actividad → indicador
- [ ] Gestión de ponderaciones tácticas + validación de suma
- [ ] Cálculo de KPI (numerador/denominador) por frecuencia
- [ ] UI: matriz de indicadores con edición inline
- **DoD:** cada actividad tiene su KPI con fórmula y frecuencia; los pesos suman ~100%.

### Fase 5 — Módulo CMI (Cuadro de Mando Integral)
- [ ] CRUD perspectivas → objetivos → indicadores → mediciones
- [ ] Captura periódica de valores (soportar varias frecuencias)
- [ ] Evaluación de semáforos (directo/inverso)
- [ ] UI: tablero por 4 perspectivas con estado semaforizado
- [ ] Gráficos por perspectiva (líneas de tendencia, cumplimiento)
- **DoD:** al ingresar un valor, el indicador se pinta verde/amarillo/rojo automáticamente.

### Fase 6 — Integración, trazabilidad y exportación
- [ ] Vincular Estrategia (matrices) → Plan → KPI → Indicador CMI
- [ ] Dashboard general (resumen de los 4 módulos)
- [ ] Exportar a Excel (openpyxl) conservando estructura de los entregables
- [ ] Exportar a PDF (informe ejecutivo)
- **DoD:** desde una estrategia se navega a su plan, su KPI y su indicador de control.

### Fase 7 — Pulido y despliegue
- [ ] Manejo de errores y mensajes de validación en UI
- [ ] Autenticación básica (login por empresa/usuario)
- [ ] Migrar a PostgreSQL (probar la misma migración Alembic)
- [ ] README con instrucciones de instalación y uso
- [ ] Despliegue (Docker opcional)
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

- **Fase actual:** Fase 2 — Módulo Matrices (sin iniciar)
- **Última tarea completada:** Fase 1 completa (12 modelos, Alembic head, 7 módulos core, 32 tests verdes)
- **Siguiente tarea:** Schemas Pydantic con validación de pesos (suma=1) y escalas
- **Bloqueos / notas:** `test_valores_control_excel` en `skip` — faltan datos reales del Excel para validar VAN≈411.622 / TIR≈28.4%. Enums `sentido` en minúscula (directo/inverso).

### Registro de avance
| Fecha | Sesión | Qué se hizo | Siguiente paso |
|-------|--------|-------------|----------------|
| 2026-07-07 | 1 | Fase 0: estructura §3, requirements, venv+install, config, database, main+/health (200), git init | Fase 1: modelos SQLAlchemy |
| 2026-07-07 | 1 | Fase 1: 12 modelos SQLAlchemy §4, Alembic init+migración `7c3f6280e8d5` (upgrade head), core {ponderacion,holmes,peyea,pestel,finanzas,kpi,semaforo}, 32 tests verdes | Fase 2: schemas + router Matrices |

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
