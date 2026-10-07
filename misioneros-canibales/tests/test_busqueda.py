import os
import sys
import unittest
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import problema as P  # noqa: E402
from busqueda import INVALIDO, OBJETIVO, REPETIDO, a_estrella, bfs  # noqa: E402
from problema import Estado  # noqa: E402


def distancias_reales():
    """Costo óptimo exacto hasta el objetivo para cada estado alcanzable (BFS inverso)."""
    dist = {P.ESTADO_OBJETIVO: 0}
    cola = deque([P.ESTADO_OBJETIVO])
    while cola:
        e = cola.popleft()
        for _a, s in P.sucesores(e):  # los movimientos son reversibles
            if s not in dist:
                dist[s] = dist[e] + 1
                cola.append(s)
    return dist


class ComprobacionesComunes:
    def ejecutar(self):
        raise NotImplementedError

    def setUp(self):
        self.r = self.ejecutar()

    def test_encuentra_solucion(self):
        self.assertTrue(self.r.encontrada)
        self.assertEqual(self.r.ruta[0].estado, P.ESTADO_INICIAL)
        self.assertTrue(P.es_objetivo(self.r.ruta[-1].estado))

    def test_solucion_optima_11_cruces(self):
        self.assertEqual(self.r.longitud, 11)
        self.assertEqual(self.r.costo, 11)

    def test_ruta_valida_y_sin_ciclos(self):
        ruta = self.r.ruta
        estados = [n.estado for n in ruta]
        self.assertEqual(len(estados), len(set(estados)), "la ruta repite estados")
        for anterior, actual in zip(ruta, ruta[1:]):
            self.assertIs(actual.padre, anterior)                     # padre correcto
            self.assertTrue(P.es_valido(actual.estado))
            self.assertEqual(P.aplicar(anterior.estado, actual.accion), actual.estado)
            self.assertEqual(actual.g, anterior.g + 1)

    def test_arbol_sin_estados_repetidos(self):
        estados = [n.estado for n in self.r.arbol]
        self.assertEqual(len(estados), len(set(estados)))

    def test_metricas_coherentes(self):
        r = self.r
        self.assertGreater(r.nodos_expandidos, 0)
        self.assertGreaterEqual(r.nodos_generados, r.nodos_expandidos)
        self.assertLessEqual(r.estados_visitados, len(P.estados_validos()))
        self.assertGreater(r.descartados_invalidos, 0)
        self.assertGreater(r.descartados_repetidos, 0)
        self.assertGreaterEqual(r.tiempo_ms, 0)
        self.assertEqual(len([p for p in r.traza if not p.es_meta]), r.nodos_expandidos)
        # cada operador aplicado queda registrado como válido o inválido
        total = sum(len(p.sucesores) for p in r.traza)
        self.assertEqual(total, r.nodos_expandidos * len(P.ACCIONES))
        invalidos = sum(1 for p in r.traza for s in p.sucesores if s.tipo == INVALIDO)
        repetidos = sum(1 for p in r.traza for s in p.sucesores if s.tipo == REPETIDO)
        self.assertEqual(invalidos, r.descartados_invalidos)
        self.assertEqual(repetidos, r.descartados_repetidos)

    def test_desde_el_objetivo(self):
        r = type(self).algoritmo(P.ESTADO_OBJETIVO)
        self.assertTrue(r.encontrada)
        self.assertEqual(r.longitud, 0)

    def test_desde_estado_intermedio_optimo(self):
        dist = distancias_reales()
        for estado in P.estados_validos():
            r = type(self).algoritmo(estado)
            if estado in dist:
                self.assertTrue(r.encontrada, estado)
                self.assertEqual(r.costo, dist[estado], estado)
            else:
                self.assertFalse(r.encontrada, estado)  # estado inalcanzable


class TestBFS(ComprobacionesComunes, unittest.TestCase):
    algoritmo = staticmethod(bfs)

    def ejecutar(self):
        return bfs()

    def test_objetivo_detectado_al_generar(self):
        ultimo = self.r.traza[-1]
        self.assertIn(OBJETIVO, [s.tipo for s in ultimo.sucesores])

    def test_valores_conocidos(self):
        self.assertEqual(self.r.nodos_expandidos, 13)
        self.assertEqual(self.r.estados_visitados, 15)


class TestAEstrella(ComprobacionesComunes, unittest.TestCase):
    algoritmo = staticmethod(a_estrella)

    def ejecutar(self):
        return a_estrella()

    def test_f_no_decrece_en_ruta(self):
        # Con h consistente, f es no decreciente a lo largo de la ruta
        fs = [n.f for n in self.r.ruta]
        self.assertEqual(fs, sorted(fs))

    def test_h_admisible_en_ruta(self):
        for n in self.r.ruta:
            self.assertLessEqual(n.h, self.r.costo - n.g)

    def test_expande_no_mas_que_bfs(self):
        self.assertLessEqual(self.r.nodos_expandidos, bfs().nodos_expandidos)

    def test_ultimo_paso_es_meta(self):
        self.assertTrue(self.r.traza[-1].es_meta)


class TestAEstrellaPersonas(ComprobacionesComunes, unittest.TestCase):
    """A* con la heurística sugerida en el README (M + C)."""

    algoritmo = staticmethod(lambda e=P.ESTADO_INICIAL: a_estrella(e, P.h_personas))

    def ejecutar(self):
        return a_estrella(heuristica=P.h_personas)

    def test_desde_estado_intermedio_optimo(self):
        # h_personas no es admisible: sólo comprobamos que encuentra solución
        dist = distancias_reales()
        for estado in P.estados_validos():
            self.assertEqual(type(self).algoritmo(estado).encontrada, estado in dist)


if __name__ == "__main__":
    unittest.main()
