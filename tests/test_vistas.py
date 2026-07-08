"""Tests basicos de vistas HTML."""


def login_demo(client):
    return client.post(
        "/login",
        data={
            "empresa_id": "",
            "username": "admin",
            "password": "admin123",
            "next_url": "/dashboard",
        },
        follow_redirects=False,
    )


def test_vistas_requieren_login(client):
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/login?next=/dashboard"


def test_login_demo_y_logout(client):
    r = login_demo(client)
    assert r.status_code == 303
    assert r.headers["location"] == "/dashboard"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "admin"

    salida = client.post("/logout", follow_redirects=False)
    assert salida.status_code == 303
    assert salida.headers["location"] == "/login"


def test_vista_planes(client):
    login_demo(client)
    r = client.get("/planes")
    assert r.status_code == 200
    assert "Planes tacticos" in r.text
    assert "Dashboard financiero" in r.text
    assert "Matriz de indicadores" in r.text
    assert "tabla-indicadores" in r.text
    assert "tabla-proyeccion" in r.text
    assert "/static/js/planes.js" in r.text


def test_index_enlaza_planes(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "/planes" in r.text
    assert "/cmi" in r.text


def test_vista_cmi(client):
    login_demo(client)
    r = client.get("/cmi")
    assert r.status_code == 200
    assert "Cuadro de Mando Integral" in r.text
    assert "tablero-cmi" in r.text
    assert "/static/js/cmi.js" in r.text


def test_vista_dashboard(client):
    login_demo(client)
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert "Dashboard general" in r.text
    assert "tablero-dashboard" in r.text
    assert "/static/js/dashboard.js" in r.text
