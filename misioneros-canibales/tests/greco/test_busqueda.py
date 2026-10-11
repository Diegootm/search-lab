"""Pruebas de la parte de Greco: algoritmos BFS y A* (busqueda.py).

Cada clase TestEtapaXX corresponde a una etapa de CODIGO_POR_ETAPAS.md.
Ejecutar desde la carpeta misioneros-canibales:

    python -m unittest discover -s tests/greco -v              (todas)
    python -m unittest discover -s tests/greco -k Etapa06 -v   (solo una etapa)
"""

import os
import sys
import unittest
from collections import deque

CARPETA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, CARPETA)
# Mientras Kendry termina problema.py se usa la copia temporal de _referencia/
# (ver GUIA_GIT.md). Si existe el archivo real, se usa el real.
sys.path.append(os.path.join(CARPETA, "_referencia"))
import problema as P  # noqa: E402
import busqueda as B  # noqa: E402


def distancias_reales():
    """Mínimo número de cruces desde cada estado hasta el objetivo (por niveles)."""
    distancia = {P.ESTADO_OBJETIVO: 0}
    cola = deque([P.ESTADO_OBJETIVO])
    while cola:
        actual = cola.popleft()
        for _accion, nuevo in P.sucesores(actual):
            if nuevo not in distancia:
                distancia[nuevo] = distancia[actual] + 1
                cola.append(nuevo)
    return distancia


def comprobar_solucion(prueba, r, cruces=11):
    """Comprobaciones comunes a BFS y A*: ruta correcta, sin ciclos y enlazada por padres."""
    prueba.assertTrue(r.encontrada)
    ruta = r.ruta
    prueba.assertEqual(ruta[0].estado, P.ESTADO_INICIAL)
    prueba.assertTrue(P.es_objetivo(ruta[-1].estado))
    prueba.assertEqual(r.longitud, cruces)
    prueba.assertEqual(r.costo, cruces)
    estados = [n.estado for n in ruta]
    prueba.assertEqual(len(estados), len(set(estados)), "la ruta repite estados (ciclo)")
    for anterior, actual in zip(ruta, ruta[1:]):
        prueba.assertIs(actual.padre, anterior)
        prueba.assertTrue(P.es_valido(actual.estado))
        prueba.assertEqual(P.aplicar(anterior.estado, actual.accion), actual.estado)
        prueba.assertEqual(actual.g, anterior.g + 1)


def comprobar_metricas(prueba, r):
    """Las métricas deben coincidir con lo que quedó registrado en la traza."""
    estados_arbol = [n.estado for n in r.arbol]
    prueba.assertEqual(len(estados_arbol), len(set(estados_arbol)), "estados repetidos en el árbol")
    prueba.assertGreaterEqual(r.nodos_generados, r.nodos_expandidos)
    prueba.assertEqual(len([p for p in r.traza if not p.es_meta]), r.nodos_expandidos)
    total = sum(len(p.sucesores) for p in r.traza)
    prueba.assertEqual(total, r.nodos_expandidos * len(P.ACCIONES))
    invalidos = sum(1 for p in r.traza for s in p.sucesores if s.tipo == B.INVALIDO)
    repetidos = sum(1 for p in r.traza for s in p.sucesores if s.tipo == B.REPETIDO)
    prueba.assertEqual(invalidos, r.descartados_invalidos)
    prueba.assertEqual(repetidos, r.descartados_repetidos)
    prueba.assertGreaterEqual(r.tiempo_ms, 0)


class TestEtapa01Estructura(unittest.TestCase):
    def test_busqueda_es_el_archivo_propio(self):
        self.assertEqual(os.path.dirname(os.path.abspath(B.__file__)), CARPETA)

    def test_tipos_de_sucesor(self):
        self.assertEqual(B.NUEVO, "nuevo")
        self.assertEqual(B.REPETIDO, "repetido")
        self.assertEqual(B.INVALIDO, "invalido")
        self.assertEqual(B.OBJETIVO, "objetivo")

class TestEtapa02Nodo(unittest.TestCase):
    def setUp(self):
        self.raiz = B.Nodo(id=1, estado=P.Estado(3, 3, 1))
        self.hijo = B.Nodo(id=2, estado=P.Estado(3, 1, 0), padre=self.raiz, accion=(0, 2),
                           g=1, h=8, profundidad=1)
        self.nieto = B.Nodo(id=3, estado=P.Estado(3, 2, 1), padre=self.hijo, accion=(0, 1),
                            g=2, h=7, profundidad=2)

    def test_valores_por_defecto(self):
        self.assertIsNone(self.raiz.padre)
        self.assertIsNone(self.raiz.accion)
        self.assertEqual((self.raiz.g, self.raiz.h, self.raiz.profundidad), (0, 0, 0))

    def test_f_es_g_mas_h(self):
        self.assertEqual(self.hijo.f, 9)
        self.assertEqual(self.raiz.f, 0)

    def test_reconstruir_la_ruta_por_padres(self):
        ruta = self.nieto.ruta()
        self.assertEqual(len(ruta), 3)
        self.assertIs(ruta[0], self.raiz)
        self.assertIs(ruta[1], self.hijo)
        self.assertIs(ruta[2], self.nieto)
        self.assertEqual(self.raiz.ruta(), [self.raiz])

class TestEtapa03Traza(unittest.TestCase):
    def test_sucesor_traza(self):
        s = B.SucesorTraza((1, 0), P.Estado(2, 3, 0), B.INVALIDO, "orilla izquierda: 3C > 2M")
        self.assertEqual(s.tipo, B.INVALIDO)
        self.assertEqual((s.g, s.h), (0, 0))

    def test_paso_expansion(self):
        raiz = B.Nodo(id=1, estado=P.ESTADO_INICIAL)
        paso = B.PasoExpansion(1, raiz, [], [(P.Estado(3, 1, 0), 1, 0)])
        self.assertEqual(paso.numero, 1)
        self.assertIs(paso.nodo, raiz)
        self.assertFalse(paso.es_meta)

class TestEtapa04Resultado(unittest.TestCase):
    def test_sin_solucion(self):
        r = B.ResultadoBusqueda("prueba", None)
        self.assertFalse(r.encontrada)
        self.assertEqual(r.ruta, [])
        self.assertEqual(r.longitud, 0)
        self.assertEqual(r.costo, 0)
        self.assertEqual(r.factor_ramificacion, 0.0)

    def test_listas_independientes(self):
        r1 = B.ResultadoBusqueda("uno", None)
        r2 = B.ResultadoBusqueda("dos", None)
        r1.arbol.append("algo")
        self.assertEqual(r2.arbol, [])
        self.assertEqual(r2.traza, [])

    def test_con_solucion(self):
        raiz = B.Nodo(id=1, estado=P.Estado(3, 3, 1))
        hijo = B.Nodo(id=2, estado=P.Estado(3, 1, 0), padre=raiz, accion=(0, 2), g=1)
        nieto = B.Nodo(id=3, estado=P.Estado(3, 2, 1), padre=hijo, accion=(0, 1), g=2)
        r = B.ResultadoBusqueda("prueba", nieto, nodos_generados=5, nodos_expandidos=2)
        self.assertTrue(r.encontrada)
        self.assertEqual(len(r.ruta), 3)
        self.assertEqual(r.longitud, 2)
        self.assertEqual(r.costo, 2)
        self.assertEqual(r.factor_ramificacion, 2.0)

class TestEtapa05Expandir(unittest.TestCase):
    def test_contador(self):
        contador = B._Contador()
        self.assertEqual([contador.siguiente() for _ in range(3)], [1, 2, 3])

    def test_expandir_el_estado_inicial(self):
        resultado = B.ResultadoBusqueda("prueba", None)
        contador = B._Contador()
        raiz = B.Nodo(id=contador.siguiente(), estado=P.ESTADO_INICIAL)
        hijos, trazas = B._expandir(raiz, contador, P.h_cruces_minimos, resultado)
        self.assertEqual([h.estado for h in hijos],
                         [P.Estado(3, 2, 0), P.Estado(3, 1, 0), P.Estado(2, 2, 0)])
        self.assertEqual(len(trazas), 5)  # se registran también los 2 inválidos
        self.assertEqual(resultado.descartados_invalidos, 2)
        self.assertEqual(resultado.nodos_generados, 3)
        for hijo in hijos:
            self.assertIs(hijo.padre, raiz)
            self.assertEqual(hijo.g, 1)
            self.assertEqual(hijo.profundidad, 1)
            self.assertEqual(hijo.h, P.h_cruces_minimos(hijo.estado))
        self.assertEqual(len({h.id for h in hijos}), 3)

class TestEtapa06BFS(unittest.TestCase):
    def setUp(self):
        self.r = B.bfs()

    def test_encuentra_la_solucion_optima(self):
        comprobar_solucion(self, self.r)

    def test_metricas_coherentes(self):
        comprobar_metricas(self, self.r)

    def test_valores_conocidos(self):
        r = self.r
        self.assertEqual(r.algoritmo, "BFS (Anchura)")
        self.assertEqual(r.nodos_generados, 29)
        self.assertEqual(r.nodos_expandidos, 13)
        self.assertEqual(r.estados_visitados, 15)
        self.assertEqual(r.descartados_repetidos, 14)
        self.assertEqual(r.descartados_invalidos, 37)
        self.assertEqual(r.max_frontera, 3)

    def test_objetivo_detectado_al_generar(self):
        tipos = [s.tipo for s in self.r.traza[-1].sucesores]
        self.assertIn(B.OBJETIVO, tipos)

    def test_desde_el_objetivo(self):
        r = B.bfs(P.ESTADO_OBJETIVO)
        self.assertTrue(r.encontrada)
        self.assertEqual(r.longitud, 0)

    def test_optima_desde_cualquier_estado(self):
        distancia = distancias_reales()
        for estado in P.estados_validos():
            r = B.bfs(estado)
            if estado in distancia:
                self.assertEqual(r.costo, distancia[estado], estado)
            else:
                self.assertFalse(r.encontrada, estado)  # estado inalcanzable

class TestEtapa07AEstrella(unittest.TestCase):
    def setUp(self):
        self.r = B.a_estrella()

    def test_encuentra_la_solucion_optima(self):
        comprobar_solucion(self, self.r)

    def test_metricas_coherentes(self):
        comprobar_metricas(self, self.r)

    def test_valores_conocidos(self):
        r = self.r
        self.assertEqual(r.algoritmo, "A* (h = cruces)")
        self.assertEqual(r.nodos_generados, 28)
        self.assertEqual(r.nodos_expandidos, 12)
        self.assertEqual(r.estados_visitados, 15)
        self.assertEqual(r.descartados_repetidos, 13)
        self.assertEqual(r.descartados_invalidos, 33)
        self.assertEqual(r.max_frontera, 3)

    def test_f_no_decrece_en_la_ruta(self):
        valores_f = [n.f for n in self.r.ruta]
        self.assertEqual(valores_f, sorted(valores_f))

    def test_h_admisible_en_la_ruta(self):
        for n in self.r.ruta:
            self.assertLessEqual(n.h, self.r.costo - n.g)

    def test_el_ultimo_paso_selecciona_la_meta(self):
        self.assertTrue(self.r.traza[-1].es_meta)

    def test_expande_no_mas_que_bfs(self):
        self.assertLessEqual(self.r.nodos_expandidos, B.bfs().nodos_expandidos)

    def test_optima_desde_cualquier_estado(self):
        distancia = distancias_reales()
        for estado in P.estados_validos():
            r = B.a_estrella(estado)
            self.assertEqual(r.encontrada, estado in distancia, estado)
            if estado in distancia:
                self.assertEqual(r.costo, distancia[estado], estado)

    def test_con_la_heuristica_personas(self):
        r = B.a_estrella(heuristica=P.h_personas)
        self.assertEqual(r.algoritmo, "A* (h = personas)")
        comprobar_solucion(self, r)

    def test_diccionario_de_algoritmos(self):
        self.assertIs(B.ALGORITMOS["bfs"], B.bfs)
        self.assertIs(B.ALGORITMOS["astar"], B.a_estrella)