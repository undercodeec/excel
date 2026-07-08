"""Tests de integracion del router CMI."""


def _crear_empresa_directa(client):
    from app.database import get_db
    from app.models.empresa import Empresa

    db = next(client.app.dependency_overrides[get_db]())
    emp = Empresa(nombre="Hacienda Celia Maria C.A.")
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp.id


def test_crud_cmi_anidado(client):
    emp_id = _crear_empresa_directa(client)
    payload = {
        "empresa_id": emp_id,
        "tipo": "financiera",
        "nombre": "Financiera",
        "objetivos": [
            {
                "descripcion": "Incrementar rentabilidad",
                "indicadores": [
                    {
                        "nombre": "Margen neto",
                        "meta": 0.18,
                        "ponderacion": 0.6,
                        "rango_min": 0.12,
                        "rango_max": 0.18,
                        "sentido": "directo",
                        "mediciones": [
                            {
                                "periodo": "2026-07",
                                "tipo_periodo": "mensual",
                                "valor": 0.16,
                            }
                        ],
                    }
                ],
            }
        ],
    }

    r = client.post("/api/cmi/perspectivas", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    perspectiva_id = body["id"]
    objetivo_id = body["objetivos"][0]["id"]
    indicador_id = body["objetivos"][0]["indicadores"][0]["id"]
    medicion_id = body["objetivos"][0]["indicadores"][0]["mediciones"][0]["id"]
    assert body["empresa_id"] == emp_id
    assert body["objetivos"][0]["indicadores"][0]["mediciones"][0]["valor"] == 0.16

    r = client.get(f"/api/cmi/perspectivas?empresa_id={emp_id}")
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1

    r = client.patch(
        f"/api/cmi/perspectivas/{perspectiva_id}",
        json={"nombre": "Perspectiva financiera"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["nombre"] == "Perspectiva financiera"

    r = client.patch(
        f"/api/cmi/objetivos/{objetivo_id}",
        json={"descripcion": "Aumentar utilidad neta"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["descripcion"] == "Aumentar utilidad neta"

    r = client.patch(
        f"/api/cmi/indicadores/{indicador_id}",
        json={"meta": 0.2, "sentido": "directo"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["meta"] == 0.2

    r = client.patch(
        f"/api/cmi/mediciones/{medicion_id}",
        json={"valor": 0.19, "periodo": "2026-08"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["valor"] == 0.19
    assert r.json()["periodo"] == "2026-08"

    r = client.delete(f"/api/cmi/perspectivas/{perspectiva_id}")
    assert r.status_code == 204
    assert client.get(f"/api/cmi/perspectivas/{perspectiva_id}").status_code == 404


def test_crear_cmi_por_nivel_y_404(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/cmi/perspectivas",
        json={"empresa_id": emp_id, "tipo": "clientes", "nombre": "Clientes"},
    )
    assert r.status_code == 201, r.text
    perspectiva_id = r.json()["id"]

    r = client.post(
        f"/api/cmi/perspectivas/{perspectiva_id}/objetivos",
        json={"descripcion": "Mejorar satisfaccion"},
    )
    assert r.status_code == 201, r.text
    objetivo_id = r.json()["id"]

    r = client.post(
        f"/api/cmi/objetivos/{objetivo_id}/indicadores",
        json={
            "nombre": "Quejas recibidas",
            "meta": 5,
            "rango_min": 5,
            "rango_max": 8,
            "sentido": "inverso",
        },
    )
    assert r.status_code == 201, r.text
    indicador_id = r.json()["id"]

    r = client.post(
        f"/api/cmi/indicadores/{indicador_id}/mediciones",
        json={"periodo": "2026-Q3", "tipo_periodo": "trimestral", "valor": 4},
    )
    assert r.status_code == 201, r.text
    assert r.json()["tipo_periodo"] == "trimestral"

    assert client.post(
        "/api/cmi/perspectivas",
        json={"empresa_id": 999, "tipo": "financiera", "nombre": "No existe"},
    ).status_code == 404
    assert client.post(
        "/api/cmi/perspectivas/999/objetivos",
        json={"descripcion": "No existe"},
    ).status_code == 404
    assert client.post(
        "/api/cmi/objetivos/999/indicadores",
        json={"nombre": "No existe", "meta": 1},
    ).status_code == 404
    assert client.post(
        "/api/cmi/indicadores/999/mediciones",
        json={"periodo": "2026-07", "valor": 1},
    ).status_code == 404


def test_cmi_valida_enums_y_ponderacion(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/cmi/perspectivas",
        json={"empresa_id": emp_id, "tipo": "otra", "nombre": "Invalida"},
    )
    assert r.status_code == 422


def test_evaluar_semaforo_cmi_directo_e_inverso(client):
    emp_id = _crear_empresa_directa(client)
    r = client.post(
        "/api/cmi/perspectivas",
        json={
            "empresa_id": emp_id,
            "tipo": "clientes",
            "nombre": "Clientes",
            "objetivos": [
                {
                    "descripcion": "Satisfaccion",
                    "indicadores": [
                        {
                            "nombre": "Satisfaccion",
                            "meta": 0.9,
                            "rango_min": 0.75,
                            "rango_max": 0.9,
                            "sentido": "directo",
                            "mediciones": [{"periodo": "2026-07", "valor": 0.82}],
                        },
                        {
                            "nombre": "Quejas",
                            "meta": 5,
                            "rango_min": 5,
                            "rango_max": 8,
                            "sentido": "inverso",
                            "mediciones": [{"periodo": "2026-07", "valor": 9}],
                        },
                    ],
                }
            ],
        },
    )
    assert r.status_code == 201, r.text
    indicadores = r.json()["objetivos"][0]["indicadores"]
    medicion_directa_id = indicadores[0]["mediciones"][0]["id"]
    medicion_inversa_id = indicadores[1]["mediciones"][0]["id"]

    r = client.get(f"/api/cmi/mediciones/{medicion_directa_id}/semaforo")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["estado"] == "AMARILLO"
    assert body["sentido"] == "directo"
    assert body["cumplimiento"] == 0.911111

    r = client.get(f"/api/cmi/mediciones/{medicion_inversa_id}/semaforo")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["estado"] == "ROJO"
    assert body["sentido"] == "inverso"

    assert client.get("/api/cmi/mediciones/999/semaforo").status_code == 404

    r = client.post(
        "/api/cmi/perspectivas",
        json={
            "empresa_id": emp_id,
            "tipo": "procesos",
            "nombre": "Procesos",
            "objetivos": [
                {
                    "descripcion": "Eficiencia",
                    "indicadores": [
                        {
                            "nombre": "Tiempo de ciclo",
                            "meta": 10,
                            "ponderacion": 1.5,
                        }
                    ],
                }
            ],
        },
    )
    assert r.status_code == 422
