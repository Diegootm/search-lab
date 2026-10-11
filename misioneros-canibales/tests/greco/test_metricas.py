"""Pruebas de la parte de Greco: métricas (metricas.py).

    python -m unittest discover -s tests/greco -k Etapa09 -v
"""

import os
import sys
import unittest

CARPETA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, CARPETA)
# Mientras Kendry termina problema.py se usa la copia temporal de _referencia/
# (ver GUIA_GIT.md). Si existe el archivo real, se usa el real.
sys.path.append(os.path.join(CARPETA, "_referencia"))
import busqueda as B  # noqa: E402
import metricas as M  # noqa: E402


class TestEtapa08EvaluacionTeorica(unittest.TestCase):
    def test_metricas_es_el_archivo_propio(self):
        self.assertEqual(os.path.dirname(os.path.abspath(M.__file__)), CARPETA)

    def test_criterios_para_ambos_algoritmos(self):
        criterios = {"Completitud", "Optimalidad", "Complejidad temporal", "Complejidad espacial"}
        self.assertEqual(set(M.EVALUACION_TEORICA), {"BFS", "A*"})
        self.assertEqual(set(M.EVALUACION_TEORICA["BFS"]), criterios)
        self.assertEqual(set(M.EVALUACION_TEORICA["A*"]), criterios)

class TestEtapa09MedirTiempo(unittest.TestCase):
    def test_estadisticas(self):
        t = M.medir_tiempo(B.bfs, 5)
        self.assertEqual(set(t), {"promedio", "mediana", "minimo", "maximo"})
        self.assertLessEqual(t["minimo"], t["mediana"])
        self.assertLessEqual(t["mediana"], t["maximo"])
        self.assertGreaterEqual(t["minimo"], 0)

    def test_ejecuta_las_repeticiones_pedidas(self):
        llamadas = []

        def algoritmo_falso():
            llamadas.append(1)
            return B.bfs()

        M.medir_tiempo(algoritmo_falso, 7)
        self.assertEqual(len(llamadas), 7)

class TestEtapa10TablaMetricas(unittest.TestCase):
    def test_filas_de_bfs(self):
        filas = M.tabla_metricas(B.bfs())
        self.assertEqual(len(filas), 11)
        valores = dict(filas)
        self.assertEqual(valores["Solución encontrada"], "Sí")
        self.assertEqual(valores["Longitud (cruces)"], "11")
        self.assertEqual(valores["Nodos generados"], "29")
        self.assertEqual(valores["Nodos expandidos"], "13")
        self.assertEqual(valores["Factor ramif. efectivo"], "2.15")
        self.assertTrue(all(isinstance(v, str) for _k, v in filas))

    def test_filas_de_a_estrella(self):
        valores = dict(M.tabla_metricas(B.a_estrella()))
        self.assertEqual(valores["Nodos expandidos"], "12")
        self.assertEqual(valores["Máx. tamaño frontera"], "3")

class TestEtapa11RutaTexto(unittest.TestCase):
    def test_ruta_de_bfs(self):
        lineas = M.ruta_texto(B.bfs())
        self.assertEqual(len(lineas), 12)
        self.assertEqual(lineas[0], " 0. (3, 3, 1)  Estado inicial")
        self.assertEqual(lineas[1], " 1. (3, 1, 0)  Cruzan 2 caníbales (izq → der)")
        self.assertEqual(lineas[-1], "11. (0, 0, 0)  Cruzan 1 misionero y 1 caníbal (izq → der)")

    def test_sin_solucion(self):
        self.assertEqual(M.ruta_texto(B.ResultadoBusqueda("vacío", None)), [])