import pytest

from app.core import finanzas


def test_proyeccion_compuesta():
    r = finanzas.proyectar(ventas_0=1000, costos_0=600, gastos_operativos_0=100, anios=5)
    assert len(r.anios) == 5
    # Año 1: ventas 1000*1.08=1080, costos 600*1.04=624
    a1 = r.anios[0]
    assert a1.ventas == 1080.0
    assert a1.costos == 624.0
    assert a1.utilidad_bruta == 456.0
    # Crecimiento monótono de ventas
    ventas = [a.ventas for a in r.anios]
    assert ventas == sorted(ventas)


def test_van_positivo():
    # Inversión 1000, flujos 500/año 3 años, wacc 10%
    v = finanzas.van(1000, [500, 500, 500], wacc=0.10)
    assert v == pytest.approx(243.426, abs=0.01)


def test_tir():
    t = finanzas.tir(1000, [500, 500, 500])
    assert t == pytest.approx(0.2338, abs=0.001)


def test_payback_interpolado():
    # Inversión 1000; acumulado llega a 1000 en año 2.0 exacto (600+400)
    p = finanzas.payback(1000, [600, 400, 500])
    assert p == pytest.approx(2.0, abs=0.001)


def test_payback_fraccion():
    # 500 + 500 = 1000 exacto en año 2; probar fracción: 400 + 400 + 400
    p = finanzas.payback(1000, [400, 400, 400])
    # tras año 2: 800; faltan 200 de 400 → 2 + 0.5 = 2.5
    assert p == pytest.approx(2.5, abs=0.001)


def test_payback_nunca():
    assert finanzas.payback(1000, [100, 100]) is None


def test_punto_equilibrio():
    pe = finanzas.punto_equilibrio(costos_fijos=400, costos_variables=300, ventas=1000)
    # 400 / (1 - 0.3) = 571.43
    assert pe == pytest.approx(571.43, abs=0.01)


@pytest.mark.skip(reason="Requiere datos reales del Excel; validar VAN≈411.622, TIR≈28.4%, payback≈2a4m")
def test_valores_control_excel():
    ...
