from app.core import semaforo
from app.core.semaforo import Estado, Sentido


def test_directo_verde():
    r = semaforo.evaluar(valor_actual=100, meta=100, rango_min=80, rango_max=100)
    assert r.estado == Estado.VERDE
    assert r.cumplimiento == 1.0


def test_directo_amarillo():
    r = semaforo.evaluar(valor_actual=90, meta=100, rango_min=80, rango_max=100)
    assert r.estado == Estado.AMARILLO


def test_directo_rojo():
    r = semaforo.evaluar(valor_actual=70, meta=100, rango_min=80, rango_max=100)
    assert r.estado == Estado.ROJO


def test_inverso_verde():
    # menos quejas es mejor; meta 5 quejas
    r = semaforo.evaluar(valor_actual=3, meta=5, rango_min=5, rango_max=10, sentido=Sentido.INVERSO)
    assert r.estado == Estado.VERDE


def test_inverso_amarillo():
    r = semaforo.evaluar(valor_actual=8, meta=5, rango_min=5, rango_max=10, sentido=Sentido.INVERSO)
    assert r.estado == Estado.AMARILLO


def test_inverso_rojo():
    r = semaforo.evaluar(valor_actual=12, meta=5, rango_min=5, rango_max=10, sentido=Sentido.INVERSO)
    assert r.estado == Estado.ROJO


def test_meta_cero():
    r = semaforo.evaluar(valor_actual=5, meta=0, rango_min=0, rango_max=0)
    assert r.cumplimiento is None
