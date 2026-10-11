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

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--traza", action="store_true", help="mostrar el proceso de expansión")
    parser.add_argument("--heuristica", choices=sorted(P.HEURISTICAS), default="cruces",
                        help="heurística para A* (por defecto: cruces, admisible)")
    parser.add_argument("--repeticiones", type=int, default=200,
                        help="repeticiones para promediar el tiempo")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        # En Windows, al redirigir a un archivo, la codificación por defecto no admite "→"
        sys.stdout.reconfigure(encoding="utf-8")

    h = P.HEURISTICAS[args.heuristica]
    ejecutar_bfs = bfs
    ejecutar_astar = lambda: a_estrella(heuristica=h)  # noqa: E731
    resultados = [ejecutar_bfs(), ejecutar_astar()]
    tiempos = [medir_tiempo(ejecutar_bfs, args.repeticiones),
               medir_tiempo(ejecutar_astar, args.repeticiones)]

    print("=" * 72)
    print(" MISIONEROS Y CANÍBALES — Comparación de metodologías de búsqueda")
    print("=" * 72)
    print(f"Estado (M, C, B): M y C en la orilla izquierda, B=1 bote a la izquierda")
    print(f"Estado inicial: {P.ESTADO_INICIAL}   Estado objetivo: {P.ESTADO_OBJETIVO}")
    print(f"Estados posibles: {len(P.todos_los_estados())}   "
          f"válidos: {len(P.estados_validos())}")

    for r in resultados:
        print(f"\n### {r.algoritmo}")
        for linea in ruta_texto(r):
            print("   " + linea)
        if args.traza:
            imprimir_traza(r)

    filas_a = tabla_metricas(resultados[0])
    filas_b = tabla_metricas(resultados[1])
    print("\n" + "-" * 72)
    print(f"{'Métrica':28s}{resultados[0].algoritmo:>20s}{resultados[1].algoritmo:>24s}")
    print("-" * 72)
    for (nombre, va), (_n, vb) in zip(filas_a, filas_b):
        if nombre.startswith("Tiempo"):
            continue
        print(f"{nombre:28s}{va:>20s}{vb:>24s}")
    print(f"{'Tiempo promedio (ms)':28s}{tiempos[0]['promedio']:>20.4f}"
          f"{tiempos[1]['promedio']:>24.4f}")
    print(f"{'Tiempo mediana (ms)':28s}{tiempos[0]['mediana']:>20.4f}"
          f"{tiempos[1]['mediana']:>24.4f}")
    print(f"  (tiempo medido sobre {args.repeticiones} ejecuciones)")

    print("\n" + "-" * 72)
    print("Parámetros teóricos de evaluación")
    print("-" * 72)
    for criterio in EVALUACION_TEORICA["BFS"]:
        print(f"{criterio:22s} BFS: {EVALUACION_TEORICA['BFS'][criterio]:30s}"
              f" A*: {EVALUACION_TEORICA['A*'][criterio]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())