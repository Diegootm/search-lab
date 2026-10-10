"""Pruebas de la parte de Gabriel: interfaz Pygame (interfaz.py y main.py).

Cada clase TestEtapaXX corresponde a una etapa de CODIGO_POR_ETAPAS.md.
Se ejecutan sin abrir ventanas (SDL_VIDEODRIVER=dummy). Desde misioneros-canibales:

    python -m unittest discover -s tests/gabriel -v              (todas)
    python -m unittest discover -s tests/gabriel -k Etapa05 -v   (solo una etapa)
"""

import os
import subprocess
import sys
import tempfile
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"          # sin ventana real
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

CARPETA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, CARPETA)
# Mientras Kendry y Greco terminan, problema/busqueda/metricas se toman de la copia
# temporal _referencia/ (ver GUIA_GIT.md). Si existe el archivo real, se usa el real.
sys.path.append(os.path.join(CARPETA, "_referencia"))

import pygame  # noqa: E402

import problema as P  # noqa: E402
import interfaz as I  # noqa: E402

pygame.display.init()
pygame.font.init()
PANTALLA = pygame.display.set_mode((I.ANCHO, I.ALTO))


def nueva_app():
    return I.App(PANTALLA)


def pulsar(app, tecla):
    """Simula que se pulsa una tecla."""
    app.manejar_evento(pygame.event.Event(pygame.KEYDOWN, key=tecla))


def clic_en_boton(prueba, app, etiqueta):
    """Simula un clic sobre el botón que tiene ese texto."""
    for boton in app.botones_activos():
        texto = boton.etiqueta() if callable(boton.etiqueta) else boton.etiqueta
        if texto == etiqueta:
            app.manejar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                                  pos=boton.rect.center))
            return
    prueba.fail(f"no existe el botón {etiqueta!r} en el modo {app.modo}")


def correr(app, segundos, dt=1 / 30):
    """Simula el paso del tiempo llamando a actualizar(), como hace el bucle principal."""
    for _ in range(int(segundos / dt)):
        app.actualizar(dt)


class TestEtapa01Estructura(unittest.TestCase):
    def test_interfaz_es_el_archivo_propio(self):
        self.assertEqual(os.path.dirname(os.path.abspath(I.__file__)), CARPETA)

    def test_tamano_de_ventana(self):
        self.assertEqual((I.ANCHO, I.ALTO), (1280, 800))
        self.assertEqual(I.FPS, 60)

    def test_colores_y_textos(self):
        for clave in ("fondo", "agua", "misionero", "canibal", "acento", "astar"):
            self.assertIn(clave, I.COL)
        self.assertEqual(len(I.COLOR_TIPO), 4)
        self.assertEqual(set(I.DESCRIPCION), {"bfs", "astar"})
        self.assertEqual(set(I.NOMBRE_H), set(P.HEURISTICAS))

    def test_archivos_del_proyecto(self):
        with open(os.path.join(CARPETA, "requirements.txt"), encoding="utf-8") as archivo:
            self.assertIn("pygame", archivo.read())
        with open(os.path.join(CARPETA, ".gitignore"), encoding="utf-8") as archivo:
            self.assertIn("__pycache__/", archivo.read())


class TestEtapa02Utilidades(unittest.TestCase):
    def test_compacto(self):
        self.assertEqual(I.compacto(P.Estado(3, 1, 0)), "(3,1,0)")

    def test_personas_en_singular_y_plural(self):
        self.assertEqual(I.personas(1, 1), "1 misionero, 1 caníbal")
        self.assertEqual(I.personas(3, 0), "3 misioneros, 0 caníbales")

    def test_suavizar(self):
        self.assertEqual(I.suavizar(0), 0)
        self.assertEqual(I.suavizar(1), 1)
        self.assertEqual(I.suavizar(0.5), 0.5)
        self.assertEqual(I.suavizar(-3), 0)
        self.assertEqual(I.suavizar(7), 1)

    def test_ruta_base(self):
        self.assertEqual(I.ruta_base(), CARPETA)

    def test_textos_y_paneles(self):
        superficie = pygame.Surface((400, 200))
        fuentes = I.Fuentes()
        rect = I.texto(superficie, "Hola", fuentes.normal, (0, 0, 0), (10, 10))
        self.assertEqual(rect.topleft, (10, 10))
        x_final = I.texto_segmentos(superficie, [("A", fuentes.peq, (0, 0, 0)),
                                                 ("B", fuentes.peq, (0, 0, 0))], (5, 5))
        self.assertGreater(x_final, 5)
        rect = I.panel(superficie, (10, 10, 100, 50), fuentes, "Título")
        self.assertEqual(rect, pygame.Rect(10, 10, 100, 50))
        self.assertEqual(superficie.get_at((50, 55))[:3], I.COL["panel"])


class TestEtapa03Boton(unittest.TestCase):
    def setUp(self):
        self.pulsado = []
        self.boton = I.Boton((10, 10, 100, 30), "Hola", lambda: self.pulsado.append(1))

    def test_clic_dentro_ejecuta_la_accion(self):
        self.assertTrue(self.boton.click((20, 20)))
        self.assertEqual(self.pulsado, [1])

    def test_clic_fuera_no_hace_nada(self):
        self.assertFalse(self.boton.click((500, 500)))
        self.assertEqual(self.pulsado, [])

    def test_boton_deshabilitado(self):
        boton = I.Boton((10, 10, 100, 30), "No", lambda: self.pulsado.append(1),
                        habilitado=lambda: False)
        self.assertFalse(boton.click((20, 20)))
        self.assertEqual(self.pulsado, [])

    def test_dibujar_en_todos_los_estados(self):
        superficie = pygame.Surface((200, 100))
        fuentes = I.Fuentes()
        seleccionado = I.Boton((10, 10, 100, 30), lambda: "Dinámico", lambda: None,
                               seleccionado=lambda: True)
        seleccionado.dibujar(superficie, fuentes.peq_b, (0, 0))
        self.assertEqual(superficie.get_at((15, 25))[:3], I.COL["acento"])
        self.boton.dibujar(superficie, fuentes.peq_b, (20, 20))  # ratón encima
        I.Boton((10, 50, 100, 30), "Pestaña", lambda: None, oscuro=True).dibujar(
            superficie, fuentes.peq_b, (0, 0))


class TestEtapa04DibujarPersonas(unittest.TestCase):
    def test_misionero_y_canibal(self):
        for tipo, color in (("M", I.COL["misionero"]), ("C", I.COL["canibal"])):
            superficie = pygame.Surface((100, 120))
            superficie.fill((255, 255, 255))
            I.dibujar_persona(superficie, 50, 100, tipo)
            self.assertEqual(superficie.get_at((45, 80))[:3], color, tipo)

    def test_tamano_reducido(self):
        superficie = pygame.Surface((100, 120))
        superficie.fill((255, 255, 255))
        I.dibujar_persona(superficie, 50, 100, "C", 0.5)
        self.assertEqual(superficie.get_at((47, 90))[:3], I.COL["canibal"])
        self.assertEqual(superficie.get_at((45, 60))[:3], (255, 255, 255))


class TestEtapa05Escena(unittest.TestCase):
    def setUp(self):
        self.superficie = pygame.Surface((840, 330))
        self.fuentes = I.Fuentes()
        self.rect = (0, 0, 840, 330)

    def test_rio_y_bote_a_la_izquierda(self):
        I.dibujar_escena(self.superficie, self.rect, P.ESTADO_INICIAL, self.fuentes)
        self.assertEqual(self.superficie.get_at((420, 315))[:3], I.COL["agua"])
        self.assertEqual(self.superficie.get_at((258, 216))[:3], I.COL["madera2"])
        self.assertNotEqual(self.superficie.get_at((484, 216))[:3], I.COL["madera2"])

    def test_bote_a_la_derecha(self):
        I.dibujar_escena(self.superficie, self.rect, P.Estado(3, 1, 0), self.fuentes)
        self.assertEqual(self.superficie.get_at((484, 216))[:3], I.COL["madera2"])

    def test_cruce_animado_y_cartel_de_objetivo(self):
        anim = {"desde": P.ESTADO_INICIAL, "hasta": P.Estado(3, 1, 0), "t": 0.5}
        I.dibujar_escena(self.superficie, self.rect, P.ESTADO_INICIAL, self.fuentes, anim,
                         "Cruzan 2 caníbales (izq → der)", "BFS")
        I.dibujar_escena(self.superficie, self.rect, P.ESTADO_OBJETIVO, self.fuentes)
        self.assertEqual(self.superficie.get_at((240, 82))[:3], I.COL["ok"])
