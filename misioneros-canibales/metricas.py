"""Métricas y evaluación comparativa de las metodologías de búsqueda."""

from __future__ import annotations

import statistics
import time
from typing import Callable

import problema as P
from busqueda import ResultadoBusqueda

# Parámetros teóricos de evaluación (Russell & Norvig).
# b = factor de ramificación, d = profundidad de la solución óptima.
EVALUACION_TEORICA = {
    "BFS": {
        "Completitud": "Sí (b finito)",
        "Optimalidad": "Sí (costos de paso iguales)",
        "Complejidad temporal": "O(b^d)",
        "Complejidad espacial": "O(b^d)",
    },
    "A*": {
        "Completitud": "Sí",
        "Optimalidad": "Sí (h admisible y consistente)",
        "Complejidad temporal": "O(b^d) peor caso; menor con buena h",
        "Complejidad espacial": "O(b^d) (guarda todos los nodos)",
    },
}

def medir_tiempo(algoritmo: Callable[[], ResultadoBusqueda], repeticiones: int = 200) -> dict:
    """Ejecuta el algoritmo varias veces y devuelve estadísticas de tiempo (ms)."""
    tiempos = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        algoritmo()
        tiempos.append((time.perf_counter() - t0) * 1000)
    return {
        "promedio": statistics.mean(tiempos),
        "mediana": statistics.median(tiempos),
        "minimo": min(tiempos),
        "maximo": max(tiempos),
    }

def tabla_metricas(resultado: ResultadoBusqueda) -> list[tuple[str, str]]:
    """Filas (nombre, valor) de las métricas de una ejecución."""
    return [
        ("Solución encontrada", "Sí" if resultado.encontrada else "No"),
        ("Longitud (cruces)", str(resultado.longitud)),
        ("Costo de la ruta", str(resultado.costo)),
        ("Nodos generados", str(resultado.nodos_generados)),
        ("Nodos expandidos", str(resultado.nodos_expandidos)),
        ("Estados visitados", str(resultado.estados_visitados)),
        ("Repetidos descartados", str(resultado.descartados_repetidos)),
        ("Inválidos descartados", str(resultado.descartados_invalidos)),
        ("Máx. tamaño frontera", str(resultado.max_frontera)),
        ("Factor ramif. efectivo", f"{resultado.factor_ramificacion:.2f}"),
        ("Tiempo (ms)", f"{resultado.tiempo_ms:.3f}"),
    ]