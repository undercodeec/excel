import pytest

from app.core import holmes


def test_ranking():
    factores = ["A", "B", "C"]
    matriz = [
        [None, 1, 1],
        [0, None, 0.5],
        [0, 0.5, None],
    ]
    r = holmes.calcular(factores, matriz)
    totales = {f.factor: f.total for f in r.filas}
    assert totales["A"] == 2.0
    assert totales["B"] == 0.5
    assert totales["C"] == 0.5
    orden = {f.factor: f.orden for f in r.filas}
    assert orden["A"] == 1


def test_celda_invalida():
    with pytest.raises(ValueError):
        holmes.calcular(["A", "B"], [[None, 2], [0, None]])


def test_matriz_no_cuadrada():
    with pytest.raises(ValueError):
        holmes.calcular(["A", "B"], [[None, 1, 0], [0, None, 1]])
