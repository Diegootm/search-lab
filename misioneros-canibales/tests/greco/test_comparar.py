"""Pruebas de la parte de Greco: comparación por consola (comparar.py).

    python -m unittest discover -s tests/greco -k Etapa13 -v
"""

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

CARPETA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, CARPETA)
# Mientras Kendry termina problema.py se usa la copia temporal de _referencia/
# (ver GUIA_GIT.md). Si existe el archivo real, se usa el real.
sys.path.append(os.path.join(CARPETA, "_referencia"))
import busqueda as B  # noqa: E402
import comparar as C  # noqa: E402


def salida_de(funcion, *argumentos):
    """Ejecuta la función y devuelve lo que imprimió en pantalla."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        funcion(*argumentos)
    return buffer.getvalue()


class TestEtapa12ImprimirTraza(unittest.TestCase):
    def test_traza_de_bfs(self):
        texto = salida_de(C.imprimir_traza, B.bfs())
        self.assertIn("--- Proceso de búsqueda: BFS (Anchura) ---", texto)
        self.assertIn("[ 1] Expande (3, 3, 1) (g=0)", texto)
        self.assertIn("(2, 3, 0)  invalido (orilla izquierda: 3C > 2M)", texto)
        self.assertIn("objetivo", texto)

    def test_traza_de_a_estrella(self):
        texto = salida_de(C.imprimir_traza, B.a_estrella())
        self.assertIn("[ 1] Expande (3, 3, 1) (g=0 h=9 f=9)", texto)
        self.assertIn("-> OBJETIVO", texto)

class TestEtapa13ProgramaComparar(unittest.TestCase):
    def test_comparacion_basica(self):
        texto = salida_de(C.main, ["--repeticiones", "3"])
        self.assertIn("Estado inicial: (3, 3, 1)   Estado objetivo: (0, 0, 0)", texto)
        self.assertIn("### BFS (Anchura)", texto)
        self.assertIn("### A* (h = cruces)", texto)
        self.assertIn("Longitud (cruces)", texto)
        self.assertIn("Parámetros teóricos de evaluación", texto)

    def test_heuristica_personas_y_traza(self):
        texto = salida_de(C.main, ["--heuristica", "personas", "--traza", "--repeticiones", "2"])
        self.assertIn("A* (h = personas)", texto)
        self.assertIn("--- Proceso de búsqueda:", texto)

    def test_devuelve_cero(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(C.main(["--repeticiones", "1"]), 0)