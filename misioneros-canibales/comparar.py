"""Ejecuta BFS y A* sobre el mismo problema e imprime la comparación por consola.

Uso:
    python comparar.py                 # compara BFS vs A* (heurística admisible)
    python comparar.py --traza         # muestra además el proceso de expansión
    python comparar.py --heuristica personas
    python comparar.py --repeticiones 1000
"""

from __future__ import annotations

import argparse
import sys

import problema as P
from busqueda import INVALIDO, ResultadoBusqueda, a_estrella, bfs
from metricas import EVALUACION_TEORICA, medir_tiempo, ruta_texto, tabla_metricas


def imprimir_traza(resultado: ResultadoBusqueda) -> None:
    print(f"\n--- Proceso de búsqueda: {resultado.algoritmo} ---")
    for paso in resultado.traza:
        n = paso.nodo
        extra = f" h={n.h} f={n.f}" if "A*" in resultado.algoritmo else ""
        if paso.es_meta:
            print(f"[{paso.numero:2d}] Se selecciona {n.estado} (g={n.g}{extra}) -> OBJETIVO")
            continue
        print(f"[{paso.numero:2d}] Expande {n.estado} (g={n.g}{extra})")
        for s in paso.sucesores:
            detalle = f" ({s.motivo})" if s.tipo == INVALIDO else ""
            print(f"       {P.nombre_accion(s.accion):6s} -> {s.estado}  {s.tipo}{detalle}")
        frontera = ", ".join(str(e) for e, _g, _h in paso.frontera) or "vacía"
        print(f"       Frontera: [{frontera}]")