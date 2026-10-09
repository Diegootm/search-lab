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