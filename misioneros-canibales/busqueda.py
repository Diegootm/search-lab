"""Algoritmos de búsqueda: Búsqueda en Anchura (BFS) y A*.

Ambos trabajan sobre la misma formulación definida en ``problema.py`` y son
búsquedas en GRAFO: llevan un conjunto de estados alcanzados para no volver a
generar estados repetidos y así evitar ciclos.

Cada ejecución devuelve un ``ResultadoBusqueda`` con:

* la ruta solución (lista de nodos desde el inicial hasta el objetivo, enlazados
  por su padre/predecesor),
* las métricas de evaluación,
* la traza de expansiones (para mostrar el proceso paso a paso en la interfaz),
* el árbol de búsqueda generado.
"""

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


class _Contador:
    def __init__(self) -> None:
        self.valor = 0

    def siguiente(self) -> int:
        self.valor += 1
        return self.valor


def _expandir(nodo: Nodo, contador: _Contador, h: Callable[[Estado], int],
              resultado: ResultadoBusqueda):
    """Genera los hijos de ``nodo``. Devuelve (hijos válidos, trazas)."""
    hijos: list[Nodo] = []
    trazas: list[SucesorTraza] = []
    for accion, estado, motivo in P.todos_los_sucesores(nodo.estado):
        if motivo is not None:
            resultado.descartados_invalidos += 1
            trazas.append(SucesorTraza(accion, estado, INVALIDO, motivo))
            continue
        hijo = Nodo(
            id=contador.siguiente(),
            estado=estado,
            padre=nodo,
            accion=accion,
            g=nodo.g + P.COSTO_CRUCE,
            h=h(estado),
            profundidad=nodo.profundidad + 1,
        )
        resultado.nodos_generados += 1
        hijos.append(hijo)
        trazas.append(SucesorTraza(accion, estado, NUEVO, None, hijo.g, hijo.h))
    return hijos, trazas


def bfs(inicial: Estado = P.ESTADO_INICIAL) -> ResultadoBusqueda:
    """Búsqueda en anchura (búsqueda en grafo, frontera FIFO).

    El test objetivo se aplica al GENERAR cada nodo (como en Russell & Norvig),
    lo que es correcto porque todos los cruces cuestan lo mismo.
    """
    resultado = ResultadoBusqueda("BFS (Anchura)", None)
    inicio = time.perf_counter()
    contador = _Contador()
    sin_heuristica: Callable[[Estado], int] = lambda _e: 0

    raiz = Nodo(id=contador.siguiente(), estado=inicial)
    resultado.nodos_generados = 1
    resultado.arbol.append(raiz)
    alcanzados: set[Estado] = {inicial}

    if P.es_objetivo(inicial):
        resultado.solucion = raiz
    else:
        frontera: deque[Nodo] = deque([raiz])
        resultado.max_frontera = 1
        while frontera and resultado.solucion is None:
            nodo = frontera.popleft()
            resultado.nodos_expandidos += 1
            hijos, trazas = _expandir(nodo, contador, sin_heuristica, resultado)
            traza_por_hijo = [t for t in trazas if t.tipo != INVALIDO]
            for hijo, traza in zip(hijos, traza_por_hijo):
                if hijo.estado in alcanzados:
                    resultado.descartados_repetidos += 1
                    traza.tipo = REPETIDO
                    continue
                alcanzados.add(hijo.estado)
                resultado.arbol.append(hijo)
                if P.es_objetivo(hijo.estado):
                    traza.tipo = OBJETIVO
                    resultado.solucion = hijo
                    break
                frontera.append(hijo)
            resultado.max_frontera = max(resultado.max_frontera, len(frontera))
            resultado.traza.append(PasoExpansion(
                resultado.nodos_expandidos, nodo, trazas,
                [(n.estado, n.g, n.h) for n in frontera]))

    resultado.estados_visitados = len(alcanzados)
    resultado.tiempo_ms = (time.perf_counter() - inicio) * 1000
    return resultado


def a_estrella(inicial: Estado = P.ESTADO_INICIAL,
               heuristica: Callable[[Estado], int] = P.h_cruces_minimos) -> ResultadoBusqueda:
    """Búsqueda A* (búsqueda en grafo, frontera ordenada por f = g + h).

    El test objetivo se aplica al EXPANDIR el nodo, condición necesaria para
    garantizar optimalidad. Desempates: menor h y luego orden de llegada (FIFO).
    """
    nombre_h = next((k for k, v in P.HEURISTICAS.items() if v is heuristica), "h")
    resultado = ResultadoBusqueda(f"A* (h = {nombre_h})", None)
    inicio = time.perf_counter()
    contador = _Contador()

    raiz = Nodo(id=contador.siguiente(), estado=inicial, h=heuristica(inicial))
    resultado.nodos_generados = 1
    resultado.arbol.append(raiz)

    mejor_g: dict[Estado, int] = {inicial: 0}
    cerrados: set[Estado] = set()
    frontera: list[tuple[int, int, int, Nodo]] = [(raiz.f, raiz.h, raiz.id, raiz)]
    resultado.max_frontera = 1

    while frontera:
        _f, _h, _id, nodo = heapq.heappop(frontera)
        if nodo.estado in cerrados or nodo.g > mejor_g.get(nodo.estado, nodo.g):
            continue  # entrada obsoleta de la cola de prioridad
        if P.es_objetivo(nodo.estado):
            resultado.solucion = nodo
            # Registrar el paso final (se selecciona el objetivo, no se expande)
            resultado.traza.append(PasoExpansion(
                resultado.nodos_expandidos + 1, nodo, [],
                [(n.estado, n.g, n.h) for *_x, n in sorted(frontera)], es_meta=True))
            break
        cerrados.add(nodo.estado)
        resultado.nodos_expandidos += 1
        hijos, trazas = _expandir(nodo, contador, heuristica, resultado)
        traza_por_hijo = [t for t in trazas if t.tipo != INVALIDO]
        for hijo, traza in zip(hijos, traza_por_hijo):
            if hijo.estado in cerrados or hijo.g >= mejor_g.get(hijo.estado, float("inf")):
                resultado.descartados_repetidos += 1
                traza.tipo = REPETIDO
                continue
            mejor_g[hijo.estado] = hijo.g
            resultado.arbol.append(hijo)
            heapq.heappush(frontera, (hijo.f, hijo.h, hijo.id, hijo))
        resultado.max_frontera = max(resultado.max_frontera, len(frontera))
        resultado.traza.append(PasoExpansion(
            resultado.nodos_expandidos, nodo, trazas,
            [(n.estado, n.g, n.h) for *_x, n in sorted(frontera)]))

    resultado.estados_visitados = len(mejor_g)
    resultado.tiempo_ms = (time.perf_counter() - inicio) * 1000
    return resultado


ALGORITMOS: dict[str, Callable[[], ResultadoBusqueda]] = {
    "bfs": bfs,
    "astar": a_estrella,
}
