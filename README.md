# Software de Planificacion Estrategica

Aplicacion web para automatizar matrices estrategicas, planes tacticos, KPI,
Cuadro de Mando Integral (CMI), dashboard general y exportacion a Excel.

Stack principal: FastAPI, SQLAlchemy, Alembic, SQLite, Jinja2, HTML/CSS,
JavaScript vanilla, Chart.js y openpyxl.

## Requisitos

- Python 3.11 o superior.
- Windows PowerShell o una terminal equivalente.
- Acceso a internet solo para instalar dependencias.

## Instalacion local

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Crear o actualizar la base de datos SQLite:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## Ejecucion

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

URLs utiles:

- App: http://127.0.0.1:8000
- Login: http://127.0.0.1:8000/login
- Salud: http://127.0.0.1:8000/health
- Docs API: http://127.0.0.1:8000/docs

Usuario demo local:

- Usuario: `admin`
- Contrasena: `admin123`

Si la base no tiene usuarios, el primer login correcto con `admin/admin123`
crea automaticamente una empresa demo y el usuario administrador.

## Configuracion

La configuracion se lee desde variables de entorno o un archivo `.env`.

Valores principales:

```env
DATABASE_URL=sqlite:///./planificacion.db
APP_NAME=Planificacion Estrategica
SECRET_KEY=cambia-esta-clave-en-produccion
```

En desarrollo se usa SQLite. La migracion a PostgreSQL queda como paso final
del plan de despliegue.

## Flujo de uso

1. Entrar con el usuario demo.
2. Crear o cargar datos por modulo:
   - Matrices: `/matrices`
   - Planes tacticos y KPI: `/planes`
   - CMI: `/cmi`
   - Resumen general: `/dashboard`
3. Revisar calculos y graficos.
4. Exportar el libro Excel desde el boton `Exportar a Excel` en `/dashboard`.

## Modulos

- Matrices estrategicas: CRUD, calculo por tipo y graficos PEYEA, radar, barras y Ansoff.
- Planes: 7 planes tacticos, estrategias, actividades, costos y dashboard financiero.
- KPI: indicadores por estrategia, ponderaciones tacticas y calculo numerador/denominador.
- CMI: perspectivas, objetivos, indicadores, mediciones y semaforos directo/inverso.
- Dashboard general: resumen de matrices, planes, KPI, CMI, semaforos y trazabilidad.
- Exportacion: descarga Excel en `/api/export/excel?empresa_id=1`.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

La suite cubre motor de calculo, routers principales, exportacion, vistas y
flujo basico de autenticacion.

## Despliegue con Docker

Artefactos incluidos:

- `Dockerfile`: imagen Python slim, instala dependencias, copia app y ejecuta migraciones.
- `docker-compose.yml`: publica el puerto `8000` y persiste SQLite en el volumen `app_data`.
- `.dockerignore`: excluye venv, cache, base local y archivos temporales.

Levantar con Docker Compose:

```powershell
docker compose up --build
```

La aplicacion quedara disponible en:

```text
http://127.0.0.1:8000
```

Configurar una clave de sesion antes de desplegar:

```powershell
$env:SECRET_KEY="clave-larga-y-privada"
docker compose up --build
```

El contenedor ejecuta automaticamente:

```sh
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Build para produccion

Archivos preparados:

- `Dockerfile`: imagen lista para prod, ejecuta migraciones y arranca FastAPI.
- `docker-compose.prod.yml`: compose para servidor.
- `.env.production.example`: plantilla de variables de entorno.

Pasos:

1. Crear el archivo real de entorno:

```powershell
Copy-Item .env.production.example .env.production
```

2. Editar `SECRET_KEY` en `.env.production`.

3. Generar la imagen:

```powershell
docker compose -f docker-compose.prod.yml build
```

4. Levantar en produccion:

```powershell
docker compose -f docker-compose.prod.yml up -d
```

5. Verificar:

```powershell
curl http://127.0.0.1:8000/health
```

## Migraciones

Crear una nueva migracion cuando cambie el modelo:

```powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "descripcion"
```

Aplicar migraciones:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Revertir una migracion:

```powershell
.\.venv\Scripts\python.exe -m alembic downgrade -1
```

## Estructura

```text
app/
  core/        funciones puras de calculo
  models/      modelos SQLAlchemy
  schemas/     schemas Pydantic
  services/    logica de negocio
  routers/     endpoints FastAPI
  export/      generacion de archivos
  templates/   vistas Jinja2
  static/      CSS y JavaScript
tests/         pruebas pytest
alembic/       migraciones de base de datos
```

## Notas operativas

- El PDF ejecutivo fue omitido por decision del usuario.
- El endpoint `/health` no requiere login.
- Las vistas principales requieren sesion; los endpoints API se mantienen
  disponibles para pruebas e integraciones locales.
- Cambiar `SECRET_KEY` antes de usar la app fuera de desarrollo.

El plan completo de avance esta en `PLAN_DESARROLLO.md`.
