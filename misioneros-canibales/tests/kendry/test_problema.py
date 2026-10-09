
"""Pruebas de la parte de Kendry: formulación del problema (problema.py).

Cada clase TestEtapaXX corresponde a una etapa de CODIGO_POR_ETAPAS.md.
Ejecutar desde la carpeta misioneros-canibales:

    python -m unittest discover -s tests/kendry -v              (todas)
    python -m unittest discover -s tests/kendry -k Etapa03 -v   (solo una etapa)
"""

import os
import sys
import unittest
from collections import deque

CARPETA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, CARPETA)

import problema as P  # noqa: E402


def estados_alcanzables():
    """Recorre el espacio de estados desde el inicial usando la función sucesor."""
    vistos = {P.ESTADO_INICIAL}
    pendientes = [P.ESTADO_INICIAL]
    while pendientes:
        actual = pendientes.pop()
        for _accion, nuevo in P.sucesores(actual):
            if nuevo not in vistos:
                vistos.add(nuevo)
                pendientes.append(nuevo)
    return vistos


def distancias_reales():
    """Mínimo número de cruces desde cada estado hasta el objetivo.

    Se recorre por niveles desde el objetivo (los movimientos son reversibles).
    """
    distancia = {P.ESTADO_OBJETIVO: 0}
    cola = deque([P.ESTADO_OBJETIVO])
    while cola:
        actual = cola.popleft()
        for _accion, nuevo in P.sucesores(actual):
            if nuevo not in distancia:
                distancia[nuevo] = distancia[actual] + 1
                cola.append(nuevo)
    return distancia


class TestEtapa01Estructura(unittest.TestCase):
    def test_problema_es_el_archivo_propio(self):
        self.assertEqual(os.path.dirname(os.path.abspath(P.__file__)), CARPETA)

    def test_constantes_del_problema(self):
        self.assertEqual(P.N_MISIONEROS, 3)
        self.assertEqual(P.N_CANIBALES, 3)
        self.assertEqual(P.CAPACIDAD_BOTE, 2)

    def test_posiciones_del_bote(self):
        self.assertEqual(P.IZQUIERDA, 1)
        self.assertEqual(P.DERECHA, 0)
