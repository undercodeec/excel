import pytest

from app.core import ponderacion


def test_calculo_basico():
    factores = [
        {"descripcion": "A", "peso": 0.5, "calificacion": 4},
        {"descripcion": "B", "peso": 0.5, "calificacion": 2},
    ]
    r = ponderacion.calcular(factores)
    assert r.factores[0].resultado == 2.0
    assert r.factores[1].resultado == 1.0
    assert r.total == 3.0
    assert r.pesos_validos is True


def test_pesos_invalidos():
    factores = [
        {"descripcion": "A", "peso": 0.3, "calificacion": 4},
        {"descripcion": "B", "peso": 0.3, "calificacion": 2},
    ]
    r = ponderacion.calcular(factores)
    assert r.pesos_validos is False


def test_calificacion_fuera_escala():
    with pytest.raises(ValueError):
        ponderacion.calcular([{"descripcion": "A", "peso": 1.0, "calificacion": 5}])


def test_escala_personalizada_aprovechabilidad():
    factores = [{"descripcion": "A", "peso": 1.0, "calificacion": 5}]
    r = ponderacion.calcular(factores, escala_min=1, escala_max=5)
    assert r.total == 5.0
