"""Pruebas de reglas, distribucion y equivalencia entre algoritmos."""

import random
import unittest

from alfa_beta import BuscadorAlfaBeta
from minimax import BuscadorMinimax
from motor import (
    DISTRIBUCION, Estado, RESULTADO_21, acciones_disponibles,
    ganador, plantarse, registrar_resultado, resultado_de_dados,
)


class PruebasJuego21(unittest.TestCase):
    def test_probabilidades(self):
        self.assertAlmostEqual(sum(p for _, p in DISTRIBUCION), 1.0)
        self.assertAlmostEqual(dict(DISTRIBUCION)[RESULTADO_21], 2 / 36)
        self.assertEqual(len(DISTRIBUCION), 11)

    def test_combinacion_21_sin_orden(self):
        self.assertEqual(resultado_de_dados(1, 2), RESULTADO_21)
        self.assertEqual(resultado_de_dados(2, 1), RESULTADO_21)
        self.assertEqual(resultado_de_dados(3, 4), 7)

    def test_victoria_inmediata(self):
        estado = registrar_resultado(Estado(), RESULTADO_21, 3)
        self.assertEqual(estado.turno, 0)
        self.assertEqual(ganador(estado), 1)

    def test_empate_de_ronda(self):
        estado = Estado(suma_j1=7, tiros_j1=1, suma_j2=7,
                        tiros_j2=1, turno=0)
        self.assertEqual(ganador(estado), 0)

    def test_plantarse_y_limite(self):
        self.assertEqual(acciones_disponibles(Estado(), 3), ("Tirar",))
        estado = registrar_resultado(Estado(), 7, 1)
        self.assertEqual(estado.turno, 2)
        self.assertEqual(plantarse(estado).turno, 0)

    def test_algoritmos_misma_decision(self):
        generador = random.Random(2026)
        for max_tiros in (1, 2, 3, 4):
            estados = [Estado()]
            for _ in range(22):
                estado = Estado()
                for _ in range(8):
                    if estado.turno == 0:
                        break
                    opciones = acciones_disponibles(estado, max_tiros)
                    if len(opciones) == 2 and generador.random() < 0.4:
                        estado = plantarse(estado)
                    else:
                        valores, probabilidades = zip(*DISTRIBUCION)
                        valor = generador.choices(valores, probabilidades)[0]
                        estado = registrar_resultado(estado, valor, max_tiros)
                    if estado.turno:
                        estados.append(estado)
            for estado in set(estados):
                minimax = BuscadorMinimax(max_tiros).elegir_accion(estado)
                alfa_beta = BuscadorAlfaBeta(max_tiros).elegir_accion(estado)
                self.assertEqual(minimax.accion, alfa_beta.accion)
                self.assertAlmostEqual(minimax.valor, alfa_beta.valor, places=8)


if __name__ == "__main__":
    unittest.main()
