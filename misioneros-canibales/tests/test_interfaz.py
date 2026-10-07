"""Pruebas de la interfaz Pygame sin ventana (SDL_VIDEODRIVER=dummy)."""

import os
import sys
import tempfile
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pygame
except ImportError:  # pragma: no cover
    pygame = None

import problema as P  # noqa: E402


@unittest.skipIf(pygame is None, "pygame no está instalado")
class TestInterfaz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import interfaz
        cls.interfaz = interfaz
        pygame.display.init()
        pygame.font.init()
        cls.pantalla = pygame.display.set_mode((interfaz.ANCHO, interfaz.ALTO))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.app = self.interfaz.App(self.pantalla)

    # utilidades -----------------------------------------------------------
    def tecla(self, key):
        self.app.manejar_evento(pygame.event.Event(pygame.KEYDOWN, key=key))

    def click(self, etiqueta):
        for b in self.app.botones_activos():
            texto = b.etiqueta() if callable(b.etiqueta) else b.etiqueta
            if texto == etiqueta:
                self.app.manejar_evento(pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN, button=1, pos=b.rect.center))
                return
        self.fail(f"no existe el botón {etiqueta!r} en el modo {self.app.modo}")

    def correr(self, segundos, dt=1 / 30):
        for _ in range(int(segundos / dt)):
            self.app.actualizar(dt)
            self.app.dibujar()

    # pruebas ----------------------------------------------------------------
    def test_simulacion_bfs_completa(self):
        self.click("BFS")
        self.click("Resolver")
        self.assertTrue(self.app.resuelto)
        self.click("Siguiente")
        self.assertIsNotNone(self.app.anim)
        self.correr(2)
        self.assertEqual(self.app.paso, 1)
        self.assertEqual(self.app.estado_sim(), P.Estado(3, 1, 0))
        self.click("Reproducir")
        self.app.i_vel = 3  # 4x
        self.correr(15)
        self.assertEqual(self.app.paso, 11)
        self.assertTrue(P.es_objetivo(self.app.estado_sim()))
        self.assertFalse(self.app.reproduciendo)
        self.tecla(pygame.K_LEFT)
        self.assertEqual(self.app.paso, 10)
        self.tecla(pygame.K_HOME)
        self.assertEqual(self.app.paso, 0)

    def test_click_en_ruta_salta_al_paso(self):
        self.click("Resolver")
        panel = self.app.PANEL_RUTA
        self.app.manejar_evento(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, button=1, pos=(panel.x + 50, panel.y + 44 + 5 * 21 + 5)))
        self.assertEqual(self.app.paso, 5)

    def test_cambiar_algoritmo_reinicia(self):
        self.click("Resolver")
        self.tecla(pygame.K_END)
        self.click("A*")
        self.assertEqual(self.app.algoritmo, "astar")
        self.assertFalse(self.app.resuelto)
        self.tecla(pygame.K_r)
        self.tecla(pygame.K_END)
        self.assertEqual(self.app.resultado().longitud, 11)
        self.assertTrue(P.es_objetivo(self.app.estado_sim()))

    def test_heuristica_alternable(self):
        self.click("A*")
        self.tecla(pygame.K_h)
        self.assertEqual(self.app.heuristica, "personas")
        self.assertIn("personas", self.app.resultado().algoritmo)
        self.tecla(pygame.K_h)
        self.assertEqual(self.app.heuristica, "cruces")

    def test_arbol_paso_a_paso(self):
        self.click("Proceso / Árbol")
        self.assertEqual(self.app.modo, "arbol")
        for alg in ("BFS", "A*"):
            self.click(alg)
            total = len(self.app.resultado().traza)
            self.click("Siguiente")
            self.assertEqual(self.app.arbol_paso, 1)
            self.click("Final")
            self.assertEqual(self.app.arbol_paso, total)
            self.click("Siguiente")
            self.assertEqual(self.app.arbol_paso, total)  # no se pasa del final
            self.click("Inicio")
            self.click("Reproducir")
            self.app.i_vel = 3
            self.correr(total * 0.25)
            self.assertEqual(self.app.arbol_paso, total)

    def test_comparacion_dibuja(self):
        self.click("Comparación")
        self.app.dibujar()
        self.assertIn("cruces", self.app._tiempos)

    def test_modo_manual(self):
        self.click("Modo manual")
        self.click("2 Misioneros")  # inválido desde el inicio
        self.assertEqual(self.app.manual_estado, P.ESTADO_INICIAL)
        self.assertEqual(self.app.manual_invalidos, 1)
        self.assertIn("inválido", self.app.manual_msg[0])
        # resolver con la ruta óptima pulsando teclas 1-5
        teclas = {(1, 0): pygame.K_1, (2, 0): pygame.K_2, (0, 1): pygame.K_3,
                  (0, 2): pygame.K_4, (1, 1): pygame.K_5}
        for nodo in self.app.resultado("bfs").ruta[1:]:
            self.tecla(teclas[nodo.accion])
            self.correr(1.5)
            self.assertEqual(self.app.manual_estado, nodo.estado)
        self.assertTrue(P.es_objetivo(self.app.manual_estado))
        self.assertIn("11 cruces", self.app.manual_msg[0])
        self.tecla(pygame.K_BACKSPACE)
        self.assertEqual(self.app.manual_estado, P.Estado(1, 1, 1))

    def test_manual_ciclo_y_pista(self):
        self.click("Modo manual")
        self.click("1 Caníbal")
        self.correr(1.5)
        self.click("1 Caníbal")   # vuelve al estado inicial: ciclo
        self.correr(1.5)
        self.assertEqual(self.app.manual_estado, P.ESTADO_INICIAL)
        self.assertIn("repetido", self.app.manual_msg[0])
        self.click("Pista (BFS)")
        self.assertIn("faltan 11", self.app.manual_msg[0])

    def test_captura_y_generacion(self):
        with tempfile.TemporaryDirectory() as tmp:
            rutas = self.interfaz.generar_capturas(self.app, tmp)
            self.assertEqual(len(rutas), 12)
            for ruta in rutas:
                self.assertGreater(os.path.getsize(ruta), 10_000)


if __name__ == "__main__":
    unittest.main()
