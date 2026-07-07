"""Tests de integración del router de matrices."""


def _crear_empresa_directa(client):
    # No hay router de empresa aún; se inserta vía sesión de la app.
    from app.database import get_db
    db = next(client.app.dependency_overrides[get_db]())
    from app.models.empresa import Empresa
    emp = Empresa(nombre="Hacienda Celia María C.A.")
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp.id


def test_crud_y_calculo_efi(client):
    emp_id = _crear_empresa_directa(client)
    payload = {
        "empresa_id": emp_id,
        "tipo": "efi",
        "nombre": "EFI prueba",
        "factores": [
            {"descripcion": "Fortaleza 1", "peso": 0.6, "calificacion": 4},
            {"descripcion": "Debilidad 1", "peso": 0.4, "calificacion": 2},
        ],
    }
    r = client.post("/api/matrices", json=payload)
    assert r.status_code == 201, r.text
    mid = r.json()["id"]

    r = client.get("/api/matrices")
    assert len(r.json()) == 1

    r = client.get(f"/api/matrices/{mid}/calculo")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3.2   # 0.6*4 + 0.4*2
    assert body["pesos_validos"] is True

    r = client.delete(f"/api/matrices/{mid}")
    assert r.status_code == 204


def test_rechaza_pesos_invalidos(client):
    emp_id = _crear_empresa_directa(client)
    payload = {
        "empresa_id": emp_id,
        "tipo": "efi",
        "nombre": "EFI mala",
        "factores": [
            {"descripcion": "A", "peso": 0.5, "calificacion": 4},
            {"descripcion": "B", "peso": 0.2, "calificacion": 2},
        ],
    }
    r = client.post("/api/matrices", json=payload)
    assert r.status_code == 422  # validación Pydantic


def test_rechaza_calificacion_fuera_escala(client):
    emp_id = _crear_empresa_directa(client)
    payload = {
        "empresa_id": emp_id,
        "tipo": "efi",
        "nombre": "EFI escala",
        "factores": [{"descripcion": "A", "peso": 1.0, "calificacion": 9}],
    }
    r = client.post("/api/matrices", json=payload)
    assert r.status_code == 422


def test_calculo_peyea(client):
    emp_id = _crear_empresa_directa(client)
    payload = {
        "empresa_id": emp_id,
        "tipo": "peyea",
        "nombre": "PEYEA prueba",
        "factores": [
            {"descripcion": "FF1", "calificacion": 4, "extra_json": {"dimension": "FF"}},
            {"descripcion": "FI1", "calificacion": 4, "extra_json": {"dimension": "FI"}},
            {"descripcion": "EE1", "calificacion": -2, "extra_json": {"dimension": "EE"}},
            {"descripcion": "VC1", "calificacion": -1, "extra_json": {"dimension": "VC"}},
        ],
    }
    r = client.post("/api/matrices", json=payload)
    assert r.status_code == 201, r.text
    mid = r.json()["id"]
    r = client.get(f"/api/matrices/{mid}/calculo")
    body = r.json()
    assert body["cuadrante"] == "Agresivo"
    assert body["x"] == 3.0
    assert body["y"] == 2.0
