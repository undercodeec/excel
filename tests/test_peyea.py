from app.core import peyea


def test_cuadrante_agresivo():
    r = peyea.calcular(ff=[4, 4], fi=[5, 3], ee=[-2, -2], vc=[-1, -1])
    assert r.ff == 4.0
    assert r.fi == 4.0
    assert r.ee == -2.0
    assert r.vc == -1.0
    assert r.x == 3.0   # FI + VC
    assert r.y == 2.0   # FF + EE
    assert r.cuadrante == "Agresivo"


def test_cuadrante_defensivo():
    r = peyea.calcular(ff=[1], fi=[1], ee=[-4], vc=[-4])
    assert r.x == -3.0
    assert r.y == -3.0
    assert r.cuadrante == "Defensivo"


def test_cuadrante_conservador():
    r = peyea.calcular(ff=[5], fi=[1], ee=[-1], vc=[-4])
    assert r.x == -3.0
    assert r.y == 4.0
    assert r.cuadrante == "Conservador"


def test_cuadrante_competitivo():
    r = peyea.calcular(ff=[1], fi=[5], ee=[-4], vc=[-1])
    assert r.x == 4.0
    assert r.y == -3.0
    assert r.cuadrante == "Competitivo"
