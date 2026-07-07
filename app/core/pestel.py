"""PESTEL: impacto × duración × signo, totalizado por categoría."""
from dataclasses import dataclass, field

CATEGORIAS = ["Politico", "Economico", "Social", "Tecnologico", "Ecologico", "Legal"]


@dataclass
class FactorPestel:
    categoria: str
    descripcion: str
    tipo: str          # "oportunidad" | "amenaza"
    impacto: int       # 1..4
    duracion: int      # 1..4
    puntaje: int


@dataclass
class ResultadoPestel:
    factores: list[FactorPestel]
    totales_categoria: dict[str, int] = field(default_factory=dict)
    total_general: int = 0


def _signo(tipo: str) -> int:
    t = tipo.strip().lower()
    if t == "oportunidad":
        return 1
    if t == "amenaza":
        return -1
    raise ValueError(f"tipo '{tipo}' inválido; use 'oportunidad' o 'amenaza'.")


def calcular(factores: list[dict]) -> ResultadoPestel:
    """puntaje = impacto * duracion * signo; totaliza por categoría.

    Cada factor: {categoria, descripcion, tipo, impacto(1..4), duracion(1..4)}.
    """
    resultados: list[FactorPestel] = []
    totales: dict[str, int] = {}
    for f in factores:
        impacto = f["impacto"]
        duracion = f["duracion"]
        if not (1 <= impacto <= 4) or not (1 <= duracion <= 4):
            raise ValueError("impacto y duracion deben estar en 1..4.")
        signo = _signo(f["tipo"])
        puntaje = impacto * duracion * signo
        cat = f["categoria"]
        resultados.append(
            FactorPestel(
                categoria=cat,
                descripcion=f.get("descripcion", ""),
                tipo=f["tipo"],
                impacto=impacto,
                duracion=duracion,
                puntaje=puntaje,
            )
        )
        totales[cat] = totales.get(cat, 0) + puntaje

    return ResultadoPestel(
        factores=resultados,
        totales_categoria=totales,
        total_general=sum(totales.values()),
    )
