from app.core import kpi


def test_kpi_normal():
    r = kpi.calcular_kpi("Cobertura", 8, 10)
    assert r.valor == 0.8
    assert "8" in r.formula


def test_division_por_cero():
    r = kpi.calcular_kpi("X", 5, 0)
    assert r.valor is None


def test_ponderaciones_validas():
    assert kpi.validar_ponderaciones([0.25, 0.25, 0.5]) is True


def test_ponderaciones_invalidas():
    assert kpi.validar_ponderaciones([0.2, 0.2]) is False
