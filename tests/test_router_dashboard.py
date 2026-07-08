"""Tests de integracion del dashboard general (Fase 6)."""


def _crear_empresa_directa(client):
    from app.database import get_db
    from app.models.empresa import Empresa

    db = next(client.app.dependency_overrides[get_db]())
    emp = Empresa(nombre="Hacienda Celia Maria C.A.")
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp.id


def _crear_matriz_directa(client, empresa_id, tipo):
    from app.database import get_db
    from app.models.enums import TipoMatriz
    from app.models.matriz import Matriz

    db = next(client.app.dependency_overrides[get_db]())
    matriz = Matriz(empresa_id=empresa_id, tipo=TipoMatriz(tipo), nombre=f"Matriz {tipo}")
    db.add(matriz)
    db.commit()
    db.refresh(matriz)
    return matriz.id


def test_dashboard_general_agrega_los_cuatro_modulos(client):
    emp_id = _crear_empresa_directa(client)
    matriz_id = _crear_matriz_directa(client, emp_id, "efi")
    _crear_matriz_directa(client, emp_id, "efe")

    # Plan con estrategia (ligada a matriz) + actividad + KPI
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "marketing",
            "estrategias": [
                {
                    "descripcion": "Abrir canales",
                    "matriz_id": matriz_id,
                    "actividades": [{"descripcion": "Mapear", "costo": 1000}],
                    "indicadores": [{"nombre": "Mercados abiertos", "ponderacion": 1.0}],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    kpi_id = r.json()["estrategias"][0]["indicadores"][0]["id"]

    # CMI con indicador verde (valor >= meta) ligado al KPI
    r = client.post(
        "/api/cmi/perspectivas",
        json={
            "empresa_id": emp_id,
            "tipo": "clientes",
            "nombre": "Clientes",
            "objetivos": [
                {
                    "descripcion": "Expandir",
                    "indicadores": [
                        {
                            "nombre": "Cobertura",
                            "meta": 0.8,
                            "rango_min": 0.6,
                            "rango_max": 0.8,
                            "kpi_id": kpi_id,
                            "mediciones": [
                                {"periodo": "2026-Q1", "valor": 0.5},
                                {"periodo": "2026-Q2", "valor": 0.9},
                            ],
                        }
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text

    r = client.get(f"/api/dashboard/general?empresa_id={emp_id}")
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["empresa_id"] == emp_id
    assert body["matrices"]["total"] == 2
    assert body["matrices"]["por_tipo"] == {"efi": 1, "efe": 1}

    assert body["planes"]["total_planes"] == 1
    assert body["planes"]["total_estrategias"] == 1
    assert body["planes"]["total_actividades"] == 1
    assert body["planes"]["total_costo"] == 1000.0
    assert body["planes"]["total_por_tipo"]["marketing"] == 1000.0

    assert body["kpi"]["total_indicadores"] == 1

    assert body["cmi"]["total_perspectivas"] == 1
    assert body["cmi"]["total_objetivos"] == 1
    assert body["cmi"]["total_indicadores"] == 1
    assert body["cmi"]["total_mediciones"] == 2
    # La última medición (0.9) supera la meta (0.8) → VERDE
    assert body["cmi"]["semaforos"]["verde"] == 1
    assert body["cmi"]["semaforos"]["rojo"] == 0

    assert body["trazabilidad"]["estrategias_con_matriz"] == 1
    assert body["trazabilidad"]["indicadores_cmi_con_kpi"] == 1


def test_dashboard_general_empresa_vacia(client):
    emp_id = _crear_empresa_directa(client)
    r = client.get(f"/api/dashboard/general?empresa_id={emp_id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["matrices"]["total"] == 0
    assert body["planes"]["total_planes"] == 0
    assert body["kpi"]["total_indicadores"] == 0
    assert body["cmi"]["total_indicadores"] == 0
    assert body["cmi"]["semaforos"]["sin_medicion"] == 0


def test_dashboard_general_empresa_inexistente(client):
    assert client.get("/api/dashboard/general?empresa_id=999").status_code == 404
