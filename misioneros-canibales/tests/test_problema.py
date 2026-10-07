import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import problema as P  # noqa: E402
from problema import Estado  # noqa: E402


class TestFormulacion(unittest.TestCase):
    def test_estado_inicial_y_objetivo(self):
        self.assertEqual(P.ESTADO_INICIAL, Estado(3, 3, 1))
        self.assertEqual(P.ESTADO_OBJETIVO, Estado(0, 0, 0))
        self.assertTrue(P.es_objetivo(Estado(0, 0, 0)))
        self.assertFalse(P.es_objetivo(Estado(0, 0, 1)))
        self.assertFalse(P.es_objetivo(P.ESTADO_INICIAL))

    def test_orilla_derecha_se_deduce(self):
        self.assertEqual(Estado(1, 2, 0).derecha, (2, 1))

    def test_operadores(self):
        self.assertEqual(set(P.ACCIONES), {(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)})
        for accion in P.ACCIONES:
            self.assertTrue(P.accion_permitida(accion))
        # El bote no viaja vacío ni con más de 2 personas
        self.assertFalse(P.accion_permitida((0, 0)))
        self.assertFalse(P.accion_permitida((2, 1)))
        self.assertFalse(P.accion_permitida((3, 0)))

    def test_conjunto_de_estados(self):
        self.assertEqual(len(P.todos_los_estados()), 32)
        self.assertEqual(len(P.estados_validos()), 20)


class TestRestricciones(unittest.TestCase):
    def test_estados_validos(self):
        for e in [Estado(3, 3, 1), Estado(3, 1, 0), Estado(2, 2, 1), Estado(0, 3, 1),
                  Estado(3, 0, 0), Estado(1, 1, 0), Estado(0, 0, 0)]:
            self.assertTrue(P.es_valido(e), e)

    def test_canibales_superan_en_izquierda(self):
        self.assertFalse(P.es_valido(Estado(2, 3, 0)))
        self.assertIn("izquierda", P.motivo_invalidez(Estado(1, 3, 0)))

    def test_canibales_superan_en_derecha(self):
        # Izquierda (2,1) segura; derecha (1,2) -> 2C > 1M
        self.assertFalse(P.es_valido(Estado(2, 1, 0)))
        self.assertIn("derecha", P.motivo_invalidez(Estado(2, 1, 0)))

    def test_sin_misioneros_no_hay_peligro(self):
        # Izquierda 0M 3C y derecha 3M 0C: válido
        self.assertTrue(P.es_valido(Estado(0, 3, 1)))

    def test_fuera_de_rango(self):
        self.assertFalse(P.es_valido(Estado(4, 3, 1)))
        self.assertFalse(P.es_valido(Estado(-1, 0, 0)))
        self.assertIsNotNone(P.motivo_invalidez(Estado(0, -1, 1)))


class TestFuncionSucesor(unittest.TestCase):
    def test_aplicar_respeta_direccion_del_bote(self):
        self.assertEqual(P.aplicar(Estado(3, 3, 1), (1, 1)), Estado(2, 2, 0))
        self.assertEqual(P.aplicar(Estado(2, 2, 0), (1, 0)), Estado(3, 2, 1))

    def test_sucesores_del_inicial(self):
        sucesores = dict(P.sucesores(P.ESTADO_INICIAL))
        self.assertEqual(sucesores, {(0, 1): Estado(3, 2, 0), (0, 2): Estado(3, 1, 0),
                                     (1, 1): Estado(2, 2, 0)})

    def test_movimientos_invalidos_del_inicial(self):
        invalidos = [(a, m) for a, _e, m in P.todos_los_sucesores(P.ESTADO_INICIAL) if m]
        self.assertEqual([a for a, _m in invalidos], [(1, 0), (2, 0)])

    def test_sucesores_siempre_validos(self):
        for estado in P.estados_validos():
            for accion, nuevo in P.sucesores(estado):
                self.assertTrue(P.es_valido(nuevo))
                self.assertNotEqual(estado.b, nuevo.b)  # el bote siempre cruza

    def test_movimiento_reversible(self):
        # Desde cualquier estado válido, aplicar la misma acción de vuelta regresa
        for estado in P.estados_validos():
            for accion, nuevo in P.sucesores(estado):
                self.assertEqual(P.aplicar(nuevo, accion), estado)


class TestHeuristicas(unittest.TestCase):
    def test_h_objetivo_es_cero(self):
        for h in P.HEURISTICAS.values():
            self.assertEqual(h(P.ESTADO_OBJETIVO), 0)

    def test_h_cruces_es_consistente(self):
        # h(n) <= costo(n, n') + h(n') para todo sucesor
        for estado in P.estados_validos():
            for _a, nuevo in P.sucesores(estado):
                self.assertLessEqual(P.h_cruces_minimos(estado),
                                     P.COSTO_CRUCE + P.h_cruces_minimos(nuevo))

    def test_h_personas_no_es_admisible(self):
        # (1,1,1): basta 1 cruce, pero h = 2
        self.assertEqual(P.h_personas(Estado(1, 1, 1)), 2)


if __name__ == "__main__":
    unittest.main()
