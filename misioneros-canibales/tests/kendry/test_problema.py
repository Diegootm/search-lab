
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



class TestEtapa02Estado(unittest.TestCase):
    def test_campos(self):
        estado = P.Estado(3, 2, 1)
        self.assertEqual((estado.m, estado.c, estado.b), (3, 2, 1))

    def test_texto(self):
        self.assertEqual(str(P.Estado(3, 2, 1)), "(3, 2, 1)")

    def test_orilla_derecha_se_deduce(self):
        self.assertEqual(P.Estado(1, 2, 0).derecha, (2, 1))
        self.assertEqual(P.Estado(3, 3, 1).derecha, (0, 0))

    def test_se_puede_usar_en_conjuntos_y_comparar(self):
        visitados = {P.Estado(3, 3, 1), P.Estado(3, 3, 1)}
        self.assertEqual(len(visitados), 1)
        self.assertEqual(P.Estado(1, 1, 0), (1, 1, 0))



class TestEtapa03InicialObjetivoOperadores(unittest.TestCase):
    def test_estado_inicial_y_objetivo(self):
        self.assertEqual(P.ESTADO_INICIAL, P.Estado(3, 3, 1))
        self.assertEqual(P.ESTADO_OBJETIVO, P.Estado(0, 0, 0))

    def test_cinco_operadores(self):
        self.assertEqual(len(P.ACCIONES), 5)
        self.assertEqual(set(P.ACCIONES), {(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)})

    def test_costo_de_cada_cruce(self):
        self.assertEqual(P.COSTO_CRUCE, 1)



class TestEtapa04TextoDeMovimientos(unittest.TestCase):
    def test_nombre_accion(self):
        self.assertEqual(P.nombre_accion((1, 0)), "1M")
        self.assertEqual(P.nombre_accion((0, 2)), "2C")
        self.assertEqual(P.nombre_accion((1, 1)), "1M 1C")

    def test_describir_movimiento_singular_y_plural(self):
        self.assertEqual(P.describir_movimiento((0, 1), P.Estado(3, 2, 0)),
                         "Cruza 1 caníbal (der → izq)")
        self.assertEqual(P.describir_movimiento((2, 0), P.Estado(3, 1, 1)),
                         "Cruzan 2 misioneros (izq → der)")
        self.assertEqual(P.describir_movimiento((1, 1), P.Estado(1, 1, 1)),
                         "Cruzan 1 misionero y 1 caníbal (izq → der)")



class TestEtapa05RangoYOrillaSegura(unittest.TestCase):
    def test_en_rango(self):
        self.assertTrue(P.en_rango(P.Estado(3, 3, 1)))
        self.assertTrue(P.en_rango(P.Estado(0, 0, 0)))
        self.assertFalse(P.en_rango(P.Estado(4, 3, 1)))
        self.assertFalse(P.en_rango(P.Estado(-1, 0, 0)))
        self.assertFalse(P.en_rango(P.Estado(0, -1, 1)))
        self.assertFalse(P.en_rango(P.Estado(0, 0, 2)))

    def test_orilla_segura(self):
        self.assertTrue(P.orilla_segura(0, 3))
        self.assertTrue(P.orilla_segura(2, 2))
        self.assertTrue(P.orilla_segura(3, 1))
        self.assertFalse(P.orilla_segura(1, 2))
        self.assertFalse(P.orilla_segura(2, 3))



class TestEtapa06Validez(unittest.TestCase):
    def test_estados_validos(self):
        for estado in [P.Estado(3, 3, 1), P.Estado(3, 1, 0), P.Estado(2, 2, 1), P.Estado(0, 3, 1),
                       P.Estado(3, 0, 0), P.Estado(1, 1, 0), P.Estado(0, 0, 0)]:
            self.assertTrue(P.es_valido(estado), estado)
            self.assertIsNone(P.motivo_invalidez(estado), estado)

    def test_canibales_superan_en_la_izquierda(self):
        self.assertFalse(P.es_valido(P.Estado(2, 3, 0)))
        self.assertEqual(P.motivo_invalidez(P.Estado(1, 3, 0)), "orilla izquierda: 3C > 1M")

    def test_canibales_superan_en_la_derecha(self):
        # izquierda (2, 1) segura, pero derecha (1, 2): 2C > 1M
        self.assertFalse(P.es_valido(P.Estado(2, 1, 0)))
        self.assertEqual(P.motivo_invalidez(P.Estado(2, 1, 0)), "orilla derecha: 2C > 1M")

    def test_sin_misioneros_no_hay_peligro(self):
        self.assertTrue(P.es_valido(P.Estado(0, 3, 1)))

    def test_fuera_de_rango(self):
        self.assertFalse(P.es_valido(P.Estado(4, 3, 1)))
        self.assertFalse(P.es_valido(P.Estado(-1, 0, 0)))
        self.assertIn("suficientes", P.motivo_invalidez(P.Estado(0, -1, 1)))



class TestEtapa07TestObjetivo(unittest.TestCase):
    def test_objetivo(self):
        self.assertTrue(P.es_objetivo(P.Estado(0, 0, 0)))

    def test_no_objetivo(self):
        self.assertFalse(P.es_objetivo(P.Estado(0, 0, 1)))  # el bote quedó a la izquierda
        self.assertFalse(P.es_objetivo(P.ESTADO_INICIAL))
        self.assertFalse(P.es_objetivo(P.Estado(1, 1, 0)))



class TestEtapa08AplicarOperadores(unittest.TestCase):
    def test_bote_a_la_izquierda_resta(self):
        self.assertEqual(P.aplicar(P.Estado(3, 3, 1), (1, 1)), P.Estado(2, 2, 0))

    def test_bote_a_la_derecha_suma(self):
        self.assertEqual(P.aplicar(P.Estado(2, 2, 0), (1, 0)), P.Estado(3, 2, 1))

    def test_aplicar_no_valida(self):
        nuevo = P.aplicar(P.Estado(3, 3, 1), (2, 0))
        self.assertEqual(nuevo, P.Estado(1, 3, 0))
        self.assertFalse(P.es_valido(nuevo))

    def test_accion_permitida(self):
        for accion in P.ACCIONES:
            self.assertTrue(P.accion_permitida(accion), accion)
        self.assertFalse(P.accion_permitida((0, 0)))  # el bote no viaja vacío
        self.assertFalse(P.accion_permitida((2, 1)))  # más de 2 personas
        self.assertFalse(P.accion_permitida((3, 0)))



class TestEtapa09FuncionSucesor(unittest.TestCase):
    def test_se_aplican_los_cinco_operadores(self):
        self.assertEqual(len(P.todos_los_sucesores(P.ESTADO_INICIAL)), 5)

    def test_sucesores_del_estado_inicial(self):
        self.assertEqual(dict(P.sucesores(P.ESTADO_INICIAL)),
                         {(0, 1): P.Estado(3, 2, 0), (0, 2): P.Estado(3, 1, 0),
                          (1, 1): P.Estado(2, 2, 0)})

    def test_movimientos_invalidos_del_estado_inicial(self):
        invalidos = [a for a, _e, motivo in P.todos_los_sucesores(P.ESTADO_INICIAL) if motivo]
        self.assertEqual(invalidos, [(1, 0), (2, 0)])

    def test_los_sucesores_siempre_son_validos(self):
        for estado in estados_alcanzables():
            for _accion, nuevo in P.sucesores(estado):
                self.assertTrue(P.es_valido(nuevo))
                self.assertNotEqual(estado.b, nuevo.b)  # el bote siempre cruza

    def test_movimientos_reversibles(self):
        for estado in estados_alcanzables():
            for accion, nuevo in P.sucesores(estado):
                self.assertEqual(P.aplicar(nuevo, accion), estado)



class TestEtapa10EspacioDeEstados(unittest.TestCase):
    def test_total_de_estados(self):
        todos = P.todos_los_estados()
        self.assertEqual(len(todos), 32)
        self.assertEqual(len(set(todos)), 32)

    def test_estados_validos(self):
        validos = P.estados_validos()
        self.assertEqual(len(validos), 20)
        self.assertTrue(all(P.es_valido(e) for e in validos))
        self.assertIn(P.ESTADO_INICIAL, validos)
        self.assertIn(P.ESTADO_OBJETIVO, validos)

    def test_estados_alcanzables_desde_el_inicial(self):
        alcanzables = estados_alcanzables()
        self.assertEqual(len(alcanzables), 16)
        self.assertTrue(alcanzables <= set(P.estados_validos()))



class TestEtapa11HeuristicaPersonas(unittest.TestCase):
    def test_valores(self):
        self.assertEqual(P.h_personas(P.ESTADO_OBJETIVO), 0)
        self.assertEqual(P.h_personas(P.ESTADO_INICIAL), 6)
        self.assertEqual(P.h_personas(P.Estado(1, 1, 1)), 2)

    def test_no_es_admisible(self):
        # Desde (1, 1, 1) basta un cruce (1M 1C), pero la heurística dice 2.
        self.assertTrue(P.es_objetivo(P.aplicar(P.Estado(1, 1, 1), (1, 1))))
        self.assertGreater(P.h_personas(P.Estado(1, 1, 1)), 1)



class TestEtapa12HeuristicaCruces(unittest.TestCase):
    def test_valores(self):
        self.assertEqual(P.h_cruces_minimos(P.ESTADO_OBJETIVO), 0)
        self.assertEqual(P.h_cruces_minimos(P.ESTADO_INICIAL), 9)
        self.assertEqual(P.h_cruces_minimos(P.Estado(1, 1, 1)), 1)
        self.assertEqual(P.h_cruces_minimos(P.Estado(3, 1, 0)), 8)
        self.assertEqual(P.h_cruces_minimos(P.Estado(0, 1, 0)), 2)
        self.assertEqual(P.h_cruces_minimos(P.Estado(0, 2, 1)), 1)

    def test_es_consistente(self):
        # h(n) <= costo(n, n') + h(n') para todo sucesor n'
        for estado in P.estados_validos():
            for _accion, nuevo in P.sucesores(estado):
                self.assertLessEqual(P.h_cruces_minimos(estado),
                                     P.COSTO_CRUCE + P.h_cruces_minimos(nuevo))

    def test_es_admisible(self):
        for estado, distancia in distancias_reales().items():
            self.assertLessEqual(P.h_cruces_minimos(estado), distancia, estado)

    def test_diccionario_de_heuristicas(self):
        self.assertIs(P.HEURISTICAS["cruces"], P.h_cruces_minimos)
        self.assertIs(P.HEURISTICAS["personas"], P.h_personas)
