"""Tests de integracion del router de trazabilidad (Fase 6)."""


def _crear_empresa_directa(client):
    from app.database import get_db
    from app.models.empresa import Empresa

    db = next(client.app.dependency_overrides[get_db]())
    emp = Empresa(nombre="Hacienda Celia Maria C.A.")
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp.id


def _crear_matriz_directa(client, empresa_id):
    from app.database import get_db
    from app.models.enums import TipoMatriz
    from app.models.matriz import Matriz

    db = next(client.app.dependency_overrides[get_db]())
    matriz = Matriz(empresa_id=empresa_id, tipo=TipoMatriz.efi, nombre="EFI diagnostico")
    db.add(matriz)
    db.commit()
    db.refresh(matriz)
    return matriz.id


def test_trazabilidad_cadena_completa(client):
    emp_id = _crear_empresa_directa(client)
    matriz_id = _crear_matriz_directa(client, emp_id)

    # Plan → Estrategia (ligada a la matriz origen) → KPI tactico
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "marketing",
            "estrategias": [
                {
                    "tipo_estrategia": "Crecimiento",
                    "descripcion": "Abrir nuevos canales",
                    "matriz_id": matriz_id,
                    "indicadores": [
                        {
                            "nombre": "Mercados abiertos",
                            "formula": "(Mercados abiertos / Mercados analizados)",
                            "frecuencia": "trimestral",
                            "ponderacion": 1.0,
                        }
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    estrategia = r.json()["estrategias"][0]
    estrategia_id = estrategia["id"]
    kpi_id = estrategia["indicadores"][0]["id"]
    assert estrategia["matriz_id"] == matriz_id

    # CMI: indicador de control vinculado al KPI tactico
    r = client.post(
        "/api/cmi/perspectivas",
        json={
            "empresa_id": emp_id,
            "tipo": "clientes",
            "nombre": "Clientes",
            "objetivos": [
                {
                    "descripcion": "Expandir mercado",
                    "indicadores": [
                        {"nombre": "Cobertura de mercado", "meta": 0.8, "kpi_id": kpi_id}
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    indicador_cmi = r.json()["objetivos"][0]["indicadores"][0]
    assert indicador_cmi["kpi_id"] == kpi_id

    # Trazabilidad desde la estrategia
    r = client.get(f"/api/trazabilidad/estrategia/{estrategia_id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["estrategia_id"] == estrategia_id
    assert body["plan"]["tipo"] == "marketing"
    assert body["plan"]["empresa_id"] == emp_id
    assert body["matriz_origen"]["id"] == matriz_id
    assert body["matriz_origen"]["tipo"] == "efi"
    assert len(body["kpis"]) == 1
    assert body["kpis"][0]["id"] == kpi_id
    assert len(body["kpis"][0]["indicadores_cmi"]) == 1
    assert body["kpis"][0]["indicadores_cmi"][0]["id"] == indicador_cmi["id"]


def test_trazabilidad_sin_matriz_ni_cmi(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "operaciones",
            "estrategias": [
                {"descripcion": "Optimizar cosecha", "indicadores": [{"nombre": "KPI suelto"}]}
            ],
        },
    )
    assert r.status_code == 201, r.text
    estrategia_id = r.json()["estrategias"][0]["id"]

    r = client.get(f"/api/trazabilidad/estrategia/{estrategia_id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["matriz_origen"] is None
    assert len(body["kpis"]) == 1
    assert body["kpis"][0]["indicadores_cmi"] == []


def test_trazabilidad_estrategia_inexistente(client):
    assert client.get("/api/trazabilidad/estrategia/999").status_code == 404
