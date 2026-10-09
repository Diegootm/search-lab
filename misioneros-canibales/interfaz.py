"""Prototipo gráfico (Pygame) del problema de los Misioneros y los Caníbales.

Pestañas:
  * Simulación       -> resuelve con BFS o A* y anima la ruta solución.
  * Proceso / Árbol  -> muestra paso a paso cómo se construye el árbol de búsqueda.
  * Comparación      -> métricas y parámetros de evaluación de BFS vs A*.
  * Modo manual      -> el usuario juega; se validan los movimientos.

Atajos: Tab cambia de pestaña, Espacio reproduce/pausa, ← → retrocede/avanza,
Inicio/Fin, B = BFS, A = A*, H = heurística, R = resolver, F12 = captura,
1-5 = movimientos en modo manual, Retroceso = deshacer, P = pista, Esc = salir.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

import problema as P  # noqa: E402
from busqueda import (INVALIDO, NUEVO, OBJETIVO, REPETIDO,  # noqa: E402
                      ResultadoBusqueda, a_estrella, bfs)
from metricas import EVALUACION_TEORICA, medir_tiempo, tabla_metricas  # noqa: E402
from problema import Estado  # noqa: E402

ANCHO, ALTO = 1280, 800
FPS = 60

COL = {
    "fondo": (235, 239, 245), "panel": (255, 255, 255), "borde": (203, 213, 225),
    "texto": (30, 41, 59), "suave": (100, 116, 139), "acento": (37, 99, 235),
    "astar": (234, 88, 12), "ok": (22, 163, 74), "error": (220, 38, 38),
    "repetido": (148, 163, 184), "meta": (202, 138, 4), "boton": (241, 245, 249),
    "boton_hover": (226, 232, 240), "barra": (30, 41, 59), "barra2": (51, 65, 85),
    "cielo1": (147, 207, 245), "cielo2": (224, 242, 254), "agua": (37, 125, 205),
    "agua2": (125, 190, 240), "pasto": (110, 170, 40), "pasto2": (77, 124, 15),
    "tierra": (146, 104, 60), "madera": (110, 66, 30), "madera2": (160, 100, 50),
    "piel": (240, 200, 160), "misionero": (37, 56, 140), "canibal": (200, 55, 35),
}
COLOR_TIPO = {NUEVO: COL["ok"], REPETIDO: COL["repetido"],
              INVALIDO: COL["error"], OBJETIVO: COL["meta"]}
NOMBRE_TIPO = {NUEVO: "nuevo", REPETIDO: "repetido", INVALIDO: "inválido", OBJETIVO: "OBJETIVO"}

DESCRIPCION = {
    "bfs": ["Búsqueda no informada.",
            "Frontera FIFO: expande por niveles.",
            "Óptima: menor número de cruces."],
    "astar": ["Búsqueda informada: f(n) = g(n) + h(n).",
              "Frontera = cola de prioridad por f.",
              "g = cruces hechos, h = estimación."],
}
NOMBRE_H = {"cruces": "cruces mínimos (admisible)", "personas": "personas M+C (README)"}