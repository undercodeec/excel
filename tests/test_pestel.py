import pytest

from app.core import pestel


def test_oportunidad_y_amenaza():
    factores = [
        {"categoria": "Economico", "descripcion": "x", "tipo": "oportunidad", "impacto": 3, "duracion": 4},
        {"categoria": "Economico", "descripcion": "y", "tipo": "amenaza", "impacto": 2, "duracion": 2},
    ]
    r = pestel.calcular(factores)
    assert r.factores[0].puntaje == 12
    assert r.factores[1].puntaje == -4
    assert r.totales_categoria["Economico"] == 8
    assert r.total_general == 8


def test_impacto_fuera_rango():
    with pytest.raises(ValueError):
        pestel.calcular([{"categoria": "Legal", "tipo": "oportunidad", "impacto": 5, "duracion": 1}])


def test_tipo_invalido():
    with pytest.raises(ValueError):
        pestel.calcular([{"categoria": "Legal", "tipo": "neutro", "impacto": 1, "duracion": 1}])
