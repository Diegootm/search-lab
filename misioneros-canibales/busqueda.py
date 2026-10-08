from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable

import problema as P
from problema import Estado

# Tipos de sucesor registrados en la traza
NUEVO = "nuevo"
REPETIDO = "repetido"
INVALIDO = "invalido"
OBJETIVO = "objetivo"


@dataclass
class Nodo:
    """Nodo del árbol de búsqueda."""

    id: int
    estado: Estado
    padre: "Nodo | None" = None
    accion: tuple[int, int] | None = None
    g: int = 0       # costo acumulado desde el inicio (número de cruces)
    h: int = 0       # valor heurístico (0 en BFS)
    profundidad: int = 0

    @property
    def f(self) -> int:
        return self.g + self.h

    def ruta(self) -> list["Nodo"]:
        """Reconstruye la ruta siguiendo los punteros al padre."""
        nodos = []
        actual: Nodo | None = self
        while actual is not None:
            nodos.append(actual)
            actual = actual.padre
        nodos.reverse()
        return nodos

@dataclass
class SucesorTraza:
    accion: tuple[int, int]
    estado: Estado
    tipo: str               # NUEVO, REPETIDO, INVALIDO u OBJETIVO
    motivo: str | None = None
    g: int = 0
    h: int = 0


@dataclass
class PasoExpansion:
    """Un paso del proceso: el nodo que se expande y lo que generó."""

    numero: int
    nodo: Nodo
    sucesores: list[SucesorTraza]
    frontera: list[tuple[Estado, int, int]]  # (estado, g, h) tras la expansión
    es_meta: bool = False  # True si en este paso se selecciona el nodo objetivo

@dataclass
class ResultadoBusqueda:
    algoritmo: str
    solucion: Nodo | None
    nodos_generados: int = 0
    nodos_expandidos: int = 0
    estados_visitados: int = 0
    descartados_repetidos: int = 0
    descartados_invalidos: int = 0
    max_frontera: int = 0
    tiempo_ms: float = 0.0
    traza: list[PasoExpansion] = field(default_factory=list)
    arbol: list[Nodo] = field(default_factory=list)

    @property
    def encontrada(self) -> bool:
        return self.solucion is not None

    @property
    def ruta(self) -> list[Nodo]:
        return self.solucion.ruta() if self.solucion else []

    @property
    def longitud(self) -> int:
        """Número de movimientos (cruces) de la solución."""
        return max(len(self.ruta) - 1, 0)

    @property
    def costo(self) -> int:
        return self.solucion.g if self.solucion else 0

    @property
    def factor_ramificacion(self) -> float:
        """Factor de ramificación efectivo promedio (generados / expandidos)."""
        if not self.nodos_expandidos:
            return 0.0
        return (self.nodos_generados - 1) / self.nodos_expandidos