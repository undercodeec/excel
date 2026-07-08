"""Tests de integracion del router de planes."""


def _crear_empresa_directa(client):
    from app.database import get_db
    from app.models.empresa import Empresa

    db = next(client.app.dependency_overrides[get_db]())
    emp = Empresa(nombre="Hacienda Celia Maria C.A.")
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp.id


def test_crud_plan_con_estrategias_y_actividades(client):
    emp_id = _crear_empresa_directa(client)
    payload = {
        "empresa_id": emp_id,
        "tipo": "marketing",
        "estrategias": [
            {
                "tipo_estrategia": "Crecimiento",
                "descripcion": "Abrir nuevos canales comerciales",
                "actividades": [
                    {
                        "descripcion": "Mapear distribuidores",
                        "responsable": "Comercial",
                        "tiempo": "30 dias",
                        "costo": 1200,
                        "tipo_cuenta": "gasto",
                    }
                ],
            }
        ],
    }

    r = client.post("/api/planes", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    plan_id = body["id"]
    estrategia_id = body["estrategias"][0]["id"]
    actividad_id = body["estrategias"][0]["actividades"][0]["id"]
    assert body["tipo"] == "marketing"
    assert body["estrategias"][0]["actividades"][0]["costo"] == 1200

    r = client.get(f"/api/planes?empresa_id={emp_id}")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.patch(f"/api/planes/{plan_id}", json={"tipo": "operaciones"})
    assert r.status_code == 200
    assert r.json()["tipo"] == "operaciones"

    r = client.patch(
        f"/api/planes/estrategias/{estrategia_id}",
        json={"descripcion": "Optimizar canales comerciales"},
    )
    assert r.status_code == 200
    assert r.json()["descripcion"] == "Optimizar canales comerciales"

    r = client.patch(
        f"/api/planes/actividades/{actividad_id}",
        json={"costo": 1500, "responsable": "Gerencia Comercial"},
    )
    assert r.status_code == 200
    assert r.json()["costo"] == 1500
    assert r.json()["responsable"] == "Gerencia Comercial"

    r = client.delete(f"/api/planes/{plan_id}")
    assert r.status_code == 204
    assert client.get(f"/api/planes/{plan_id}").status_code == 404


def test_crear_estrategia_y_actividad_anidadas(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post("/api/planes", json={"empresa_id": emp_id, "tipo": "financiero"})
    assert r.status_code == 201, r.text
    plan_id = r.json()["id"]

    r = client.post(
        f"/api/planes/{plan_id}/estrategias",
        json={"tipo_estrategia": "Rentabilidad", "descripcion": "Reducir costos"},
    )
    assert r.status_code == 201, r.text
    estrategia_id = r.json()["id"]

    r = client.post(
        f"/api/planes/estrategias/{estrategia_id}/actividades",
        json={
            "descripcion": "Negociar insumos",
            "responsable": "Compras",
            "tiempo": "15 dias",
            "costo": 0,
            "tipo_cuenta": "ahorro",
        },
    )
    assert r.status_code == 201, r.text
    assert r.json()["descripcion"] == "Negociar insumos"


def test_crud_indicadores_por_estrategia(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "marketing",
            "estrategias": [
                {
                    "tipo_estrategia": "Crecimiento",
                    "descripcion": "Abrir mercados",
                    "actividades": [{"descripcion": "Mapear distribuidores"}],
                    "indicadores": [
                        {
                            "tipo": "resultado",
                            "nombre": "Mercados identificados",
                            "formula": "(Mercados identificados / Mercados analizados)",
                            "frecuencia": "mensual",
                            "ponderacion": 0.4,
                        }
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    estrategia = r.json()["estrategias"][0]
    estrategia_id = estrategia["id"]
    indicador_id = estrategia["indicadores"][0]["id"]
    assert estrategia["actividades"][0]["descripcion"] == "Mapear distribuidores"
    assert estrategia["indicadores"][0]["ponderacion"] == 0.4

    r = client.post(
        f"/api/planes/estrategias/{estrategia_id}/indicadores",
        json={
            "tipo": "gestion",
            "nombre": "Reuniones comerciales",
            "formula": "(Reuniones realizadas / Reuniones planificadas)",
            "frecuencia": "trimestral",
            "ponderacion": 0.6,
        },
    )
    assert r.status_code == 201, r.text
    segundo_indicador_id = r.json()["id"]
    assert r.json()["estrategia_id"] == estrategia_id

    r = client.get(f"/api/planes/estrategias/{estrategia_id}/indicadores")
    assert r.status_code == 200, r.text
    assert [i["nombre"] for i in r.json()] == [
        "Mercados identificados",
        "Reuniones comerciales",
    ]

    r = client.get(f"/api/planes/indicadores/{indicador_id}")
    assert r.status_code == 200, r.text
    assert r.json()["formula"] == "(Mercados identificados / Mercados analizados)"

    r = client.patch(
        f"/api/planes/indicadores/{segundo_indicador_id}",
        json={"ponderacion": 0.55, "frecuencia": "mensual"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["ponderacion"] == 0.55
    assert r.json()["frecuencia"] == "mensual"

    r = client.delete(f"/api/planes/indicadores/{indicador_id}")
    assert r.status_code == 204
    assert client.get(f"/api/planes/indicadores/{indicador_id}").status_code == 404


def test_indicadores_validan_estrategia_y_ponderacion(client):
    r = client.post(
        "/api/planes/estrategias/999/indicadores",
        json={"nombre": "No existe", "ponderacion": 0.5},
    )
    assert r.status_code == 404

    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "control",
            "estrategias": [{"descripcion": "Controlar procesos"}],
        },
    )
    assert r.status_code == 201, r.text
    estrategia_id = r.json()["estrategias"][0]["id"]

    r = client.post(
        f"/api/planes/estrategias/{estrategia_id}/indicadores",
        json={"nombre": "Peso invalido", "ponderacion": 1.2},
    )
    assert r.status_code == 422


def test_validar_ponderaciones_tacticas_por_estrategia(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "operaciones",
            "estrategias": [
                {
                    "descripcion": "Mejorar productividad",
                    "indicadores": [
                        {"nombre": "Rendimiento por hectarea", "ponderacion": 0.7},
                        {"nombre": "Cumplimiento de cosecha", "ponderacion": 0.3},
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    estrategia_id = r.json()["estrategias"][0]["id"]
    indicador_id = r.json()["estrategias"][0]["indicadores"][1]["id"]

    r = client.get(
        f"/api/planes/estrategias/{estrategia_id}/indicadores/ponderaciones"
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_ponderacion"] == 1.0
    assert body["diferencia"] == 0.0
    assert body["valido"] is True
    assert len(body["indicadores"]) == 2

    r = client.patch(
        f"/api/planes/indicadores/{indicador_id}",
        json={"ponderacion": 0.2},
    )
    assert r.status_code == 200, r.text

    r = client.get(
        f"/api/planes/estrategias/{estrategia_id}/indicadores/ponderaciones"
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_ponderacion"] == 0.9
    assert body["diferencia"] == 0.1
    assert body["valido"] is False


def test_validar_ponderaciones_tacticas_estrategia_inexistente(client):
    r = client.get("/api/planes/estrategias/999/indicadores/ponderaciones")
    assert r.status_code == 404


def test_calcular_kpi_por_indicador_y_frecuencia(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "marketing",
            "estrategias": [
                {
                    "descripcion": "Desarrollar canales",
                    "indicadores": [
                        {
                            "nombre": "Mercados evaluados",
                            "formula": "(Mercados evaluados / Mercados objetivo)",
                            "frecuencia": "mensual",
                            "ponderacion": 1,
                        }
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    indicador_id = r.json()["estrategias"][0]["indicadores"][0]["id"]

    r = client.post(
        f"/api/planes/indicadores/{indicador_id}/calcular",
        json={
            "numerador": 8,
            "denominador": 10,
            "periodo": "2026-07",
            "tipo_periodo": "mensual",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["indicador_id"] == indicador_id
    assert body["nombre"] == "Mercados evaluados"
    assert body["frecuencia"] == "mensual"
    assert body["periodo"] == "2026-07"
    assert body["tipo_periodo"] == "mensual"
    assert body["valor"] == 0.8
    assert body["formula"] == "(Mercados evaluados / Mercados objetivo)"


def test_calcular_kpi_division_por_cero_y_404(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "control",
            "estrategias": [
                {
                    "descripcion": "Controlar gestion",
                    "indicadores": [{"nombre": "Cumplimiento", "ponderacion": 1}],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    indicador_id = r.json()["estrategias"][0]["indicadores"][0]["id"]

    r = client.post(
        f"/api/planes/indicadores/{indicador_id}/calcular",
        json={"numerador": 5, "denominador": 0, "periodo": "Q3"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["valor"] is None

    r = client.post(
        "/api/planes/indicadores/999/calcular",
        json={"numerador": 1, "denominador": 1},
    )
    assert r.status_code == 404


def test_rechaza_costo_negativo(client):
    emp_id = _crear_empresa_directa(client)
    payload = {
        "empresa_id": emp_id,
        "tipo": "compras",
        "estrategias": [
            {
                "descripcion": "Mejorar abastecimiento",
                "actividades": [{"descripcion": "Comprar fertilizante", "costo": -1}],
            }
        ],
    }
    r = client.post("/api/planes", json=payload)
    assert r.status_code == 422


def test_rechaza_plan_con_empresa_inexistente(client):
    r = client.post("/api/planes", json={"empresa_id": 999, "tipo": "financiero"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Empresa no encontrada"


def test_404_en_recursos_inexistentes(client):
    assert client.get("/api/planes/999").status_code == 404
    assert client.post(
        "/api/planes/999/estrategias",
        json={"descripcion": "No existe"},
    ).status_code == 404
    assert client.post(
        "/api/planes/estrategias/999/actividades",
        json={"descripcion": "No existe"},
    ).status_code == 404
    assert client.get("/api/planes/consolidado/totales?empresa_id=999").status_code == 404


def test_totalizacion_por_plan_y_consolidado(client):
    emp_id = _crear_empresa_directa(client)
    payload_marketing = {
        "empresa_id": emp_id,
        "tipo": "marketing",
        "estrategias": [
            {
                "descripcion": "Abrir mercado local",
                "actividades": [
                    {"descripcion": "Campania digital", "costo": 1000},
                    {"descripcion": "Rueda de negocios", "costo": 500.5},
                    {"descripcion": "Gestion interna"},
                ],
            },
            {
                "descripcion": "Mejorar marca",
                "actividades": [{"descripcion": "Diseno de material", "costo": 250}],
            },
        ],
    }
    payload_compras = {
        "empresa_id": emp_id,
        "tipo": "compras",
        "estrategias": [
            {
                "descripcion": "Optimizar proveedores",
                "actividades": [{"descripcion": "Auditoria", "costo": 300}],
            }
        ],
    }

    r = client.post("/api/planes", json=payload_marketing)
    assert r.status_code == 201, r.text
    marketing_id = r.json()["id"]
    r = client.post("/api/planes", json=payload_compras)
    assert r.status_code == 201, r.text

    r = client.get(f"/api/planes/{marketing_id}/totales")
    assert r.status_code == 200, r.text
    total_plan = r.json()
    assert total_plan["total_costo"] == 1750.5
    assert total_plan["estrategias"][0]["total_costo"] == 1500.5
    assert total_plan["estrategias"][0]["actividades"][2]["costo"] == 0

    r = client.get(f"/api/planes/consolidado/totales?empresa_id={emp_id}")
    assert r.status_code == 200, r.text
    consolidado = r.json()
    assert consolidado["total_costo"] == 2050.5
    assert consolidado["total_por_tipo"]["marketing"] == 1750.5
    assert consolidado["total_por_tipo"]["compras"] == 300
    assert len(consolidado["planes"]) == 2


def test_totalizacion_plan_inexistente(client):
    assert client.get("/api/planes/999/totales").status_code == 404


def test_actualizar_estrategia_permite_limpiar_tipo(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "marketing",
            "estrategias": [
                {
                    "tipo_estrategia": "Crecimiento",
                    "descripcion": "Abrir canales",
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    estrategia_id = r.json()["estrategias"][0]["id"]

    r = client.patch(
        f"/api/planes/estrategias/{estrategia_id}",
        json={"tipo_estrategia": None},
    )
    assert r.status_code == 200, r.text
    assert r.json()["tipo_estrategia"] is None


def test_dashboard_financiero_usa_total_planes_como_gasto_base(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/planes",
        json={
            "empresa_id": emp_id,
            "tipo": "financiero",
            "estrategias": [
                {
                    "descripcion": "Plan de rentabilidad",
                    "actividades": [
                        {"descripcion": "Implementar control", "costo": 1000},
                        {"descripcion": "Capacitacion", "costo": 500},
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text

    r = client.get(
        "/api/planes/dashboard/financiero",
        params={
            "empresa_id": emp_id,
            "ventas_base": 10000,
            "costos_base": 5000,
            "costos_fijos": 2000,
            "costos_variables": 3000,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_planes"] == 1500
    assert body["gastos_operativos_base"] == 1500
    assert body["inversion_inicial"] == 1500
    assert body["premisas"]["inflacion"] == 0.04
    assert len(body["proyeccion"]) == 5
    assert body["proyeccion"][0]["ventas"] == 10800
    assert body["proyeccion"][0]["gastos_operativos"] == 1560
    assert body["flujos"][0] == body["proyeccion"][0]["utilidad_neta"]
    assert body["metricas"]["van"] > 0
    assert body["metricas"]["tir"] is not None
    assert body["metricas"]["payback"] is not None
    assert body["metricas"]["punto_equilibrio"] == 2857.14


def test_dashboard_financiero_usa_premisas_de_empresa(client):
    from app.database import get_db
    from app.models.empresa import PremisasFinancieras

    emp_id = _crear_empresa_directa(client)
    db = next(client.app.dependency_overrides[get_db]())
    db.add(
        PremisasFinancieras(
            empresa_id=emp_id,
            inflacion=0.10,
            crecimiento_ventas=0.20,
            impuestos=0.30,
            wacc=0.15,
        )
    )
    db.commit()

    r = client.get(
        "/api/planes/dashboard/financiero",
        params={
            "empresa_id": emp_id,
            "ventas_base": 1000,
            "costos_base": 400,
            "gastos_operativos_base": 100,
            "inversion_inicial": 500,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["premisas"] == {
        "inflacion": 0.10,
        "crecimiento_ventas": 0.20,
        "impuestos": 0.30,
        "wacc": 0.15,
    }
    assert body["proyeccion"][0]["ventas"] == 1200
    assert body["proyeccion"][0]["costos"] == 440
    assert body["proyeccion"][0]["gastos_operativos"] == 110
    assert body["proyeccion"][0]["utilidad_neta"] == 455


def test_dashboard_financiero_empresa_inexistente(client):
    r = client.get(
        "/api/planes/dashboard/financiero",
        params={"empresa_id": 999, "ventas_base": 1000, "costos_base": 400},
    )
    assert r.status_code == 404
