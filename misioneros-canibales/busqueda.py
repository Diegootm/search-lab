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