"""Matriz Holmes: comparación pareada de N factores."""
from dataclasses import dataclass

VALORES_VALIDOS = {0.0, 0.5, 1.0}


@dataclass
class FilaHolmes:
    factor: str
    total: float
    orden: int


@dataclass
class ResultadoHolmes:
    filas: list[FilaHolmes]
    matriz: list[list[float | None]]


def _validar_matriz(matriz: list[list[float | None]]) -> None:
    n = len(matriz)
    for i, fila in enumerate(matriz):
        if len(fila) != n:
            raise ValueError("La matriz Holmes debe ser cuadrada (NxN).")
        for j, celda in enumerate(fila):
            if i == j:
                continue  # diagonal vacía
            if celda not in VALORES_VALIDOS:
                raise ValueError(f"Celda ({i},{j})={celda} inválida; use 0, 0.5 o 1.")


def calcular(factores: list[str], matriz: list[list[float | None]]) -> ResultadoHolmes:
    """total_i = Σ_j celda(i,j) (diagonal ignorada); orden por total descendente."""
    if len(factores) != len(matriz):
        raise ValueError("Número de factores no coincide con el tamaño de la matriz.")
    _validar_matriz(matriz)

    totales = [
        (factores[i], round(sum(c for j, c in enumerate(fila) if j != i and c is not None), 6))
        for i, fila in enumerate(matriz)
    ]
    ordenados = sorted(range(len(totales)), key=lambda i: totales[i][1], reverse=True)
    rank = {idx: pos + 1 for pos, idx in enumerate(ordenados)}

    filas = [
        FilaHolmes(factor=totales[i][0], total=totales[i][1], orden=rank[i])
        for i in range(len(totales))
    ]
    return ResultadoHolmes(filas=filas, matriz=matriz)
