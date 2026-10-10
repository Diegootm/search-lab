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


class TestEtapa06AppBase(unittest.TestCase):
    def setUp(self):
        self.app = nueva_app()

    def test_valores_iniciales(self):
        app = self.app
        self.assertEqual((app.modo, app.algoritmo, app.heuristica), ("sim", "bfs", "cruces"))
        self.assertEqual(app.vel, 1.0)
        self.assertFalse(app.resuelto)
        self.assertEqual(app.paso, 0)

    def test_resultados_de_los_algoritmos(self):
        r = self.app.resultado("bfs")
        self.assertEqual(r.longitud, 11)
        self.assertIs(self.app.resultado("bfs"), r)  # se guarda en caché
        self.assertEqual(self.app.resultado("astar").nodos_expandidos, 12)

    def test_antes_de_resolver(self):
        self.assertEqual(self.app.ruta(), [])
        self.assertEqual(self.app.n_pasos(), 0)
        self.assertEqual(self.app.estado_sim(), P.ESTADO_INICIAL)
        self.assertEqual(self.app.nombre_algoritmo(), "BFS (Anchura)")
        self.assertEqual(self.app.nombre_algoritmo("astar"), "A* (A estrella)")

    def test_despues_de_resolver(self):
        self.app.resuelto = True
        self.assertEqual(self.app.n_pasos(), 11)
        self.app.paso = 1
        self.assertEqual(self.app.estado_sim(), P.Estado(3, 1, 0))


class TestEtapa07Acciones(unittest.TestCase):
    def setUp(self):
        self.app = nueva_app()

    def test_resolver_y_avanzar(self):
        app = self.app
        app.resolver()
        self.assertTrue(app.resuelto)
        self.assertIsNotNone(app.toast)
        app.avanzar()
        self.assertIsNotNone(app.anim)
        app.terminar_anim()
        self.assertEqual(app.paso, 1)
        self.assertEqual(app.estado_sim(), P.Estado(3, 1, 0))

    def test_navegar_por_la_ruta(self):
        app = self.app
        app.resolver()
        app.ir_final()
        self.assertEqual(app.paso, 11)
        self.assertTrue(P.es_objetivo(app.estado_sim()))
        app.retroceder()
        self.assertEqual(app.paso, 10)
        app.ir_inicio()
        app.retroceder()
        self.assertEqual(app.paso, 0)

    def test_cambiar_algoritmo_y_heuristica(self):
        app = self.app
        app.resolver()
        app.seleccionar_algoritmo("astar")
        self.assertEqual(app.algoritmo, "astar")
        self.assertFalse(app.resuelto)
        app.alternar_heuristica()
        self.assertEqual(app.heuristica, "personas")
        self.assertIn("personas", app.resultado().algoritmo)
        app.alternar_heuristica()
        self.assertEqual(app.heuristica, "cruces")

    def test_velocidad(self):
        valores = []
        for _ in range(4):
            self.app.cambiar_velocidad()
            valores.append(self.app.vel)
        self.assertEqual(valores, [2.0, 4.0, 0.5, 1.0])

    def test_pasos_del_arbol(self):
        app = self.app
        total = len(app.resultado().traza)
        app.arbol_mover(1)
        self.assertEqual(app.arbol_paso, 1)
        app.arbol_final()
        self.assertEqual(app.arbol_paso, total)
        app.arbol_mover(1)
        self.assertEqual(app.arbol_paso, total)  # no se pasa del final
        app.arbol_mover(-100)
        self.assertEqual(app.arbol_paso, 0)

    def test_reproducir_y_cambiar_de_modo(self):
        app = self.app
        app.alternar_reproduccion()
        self.assertTrue(app.resuelto)
        self.assertTrue(app.reproduciendo)
        app.cambiar_modo("arbol")
        self.assertFalse(app.reproduciendo)
        app.siguiente_modo()
        self.assertEqual(app.modo, "comp")
        app.siguiente_modo()
        app.siguiente_modo()
        self.assertEqual(app.modo, "sim")


class TestEtapa08ModoManual(unittest.TestCase):
    def setUp(self):
        self.app = nueva_app()

    def test_estado_inicial_del_juego(self):
        self.assertEqual(self.app.manual_estado, P.ESTADO_INICIAL)
        self.assertEqual(self.app.manual_hist, [])
        self.assertEqual(self.app.manual_invalidos, 0)

    def test_movimiento_invalido(self):
        self.app.mover_manual((2, 0))
        self.assertEqual(self.app.manual_estado, P.ESTADO_INICIAL)
        self.assertEqual(self.app.manual_invalidos, 1)
        self.assertIn("inválido", self.app.manual_msg[0])
        self.assertIsNone(self.app.anim)

    def test_movimiento_valido_y_ciclo(self):
        app = self.app
        app.mover_manual((0, 1))
        self.assertIsNotNone(app.anim)
        app.terminar_anim()
        self.assertEqual(app.manual_estado, P.Estado(3, 2, 0))
        app.mover_manual((0, 1))
        app.terminar_anim()
        self.assertEqual(app.manual_estado, P.ESTADO_INICIAL)
        self.assertIn("repetido", app.manual_msg[0])

    def test_deshacer_y_pista(self):
        app = self.app
        app.mover_manual((0, 2))
        app.terminar_anim()
        app.deshacer_manual()
        self.assertEqual(app.manual_estado, P.ESTADO_INICIAL)
        app.pista()
        self.assertIn("Pista (BFS)", app.manual_msg[0])
        self.assertIn("faltan 11", app.manual_msg[0])

    def test_reiniciar(self):
        app = self.app
        app.mover_manual((1, 1))
        app.terminar_anim()
        app.reiniciar_manual()
        self.assertEqual(app.manual_estado, P.ESTADO_INICIAL)
        self.assertEqual(app.manual_hist, [])

    def test_captura(self):
        original = I.ruta_base
        with tempfile.TemporaryDirectory() as carpeta:
            I.ruta_base = lambda: carpeta
            try:
                ruta = self.app.captura("prueba.png")
                self.assertTrue(os.path.exists(ruta))
            finally:
                I.ruta_base = original


class TestEtapa09BotonesYEventos(unittest.TestCase):
    def setUp(self):
        self.app = nueva_app()

    def test_botones_de_cada_modo(self):
        self.assertEqual(set(self.app.botones), {"superior", "sim", "arbol", "comp", "manual"})
        self.assertEqual(len(self.app.botones["superior"]), 4)

    def test_resolver_con_clic_y_avanzar_con_teclado(self):
        clic_en_boton(self, self.app, "Resolver")
        self.assertTrue(self.app.resuelto)
        pulsar(self.app, pygame.K_RIGHT)
        self.assertIsNotNone(self.app.anim)
        correr(self.app, 2)
        self.assertEqual(self.app.paso, 1)

    def test_reproduccion_automatica(self):
        clic_en_boton(self, self.app, "Reproducir")
        self.app.i_vel = 3  # velocidad 4x
        correr(self.app, 15)
        self.assertEqual(self.app.paso, 11)
        self.assertFalse(self.app.reproduciendo)

    def test_clic_en_una_fila_de_la_ruta(self):
        clic_en_boton(self, self.app, "Resolver")
        panel = self.app.PANEL_RUTA
        self.app.manejar_evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                                   pos=(panel.x + 50, panel.y + 44 + 5 * 21 + 5)))
        self.assertEqual(self.app.paso, 5)

    def test_cambiar_de_pestana(self):
        pulsar(self.app, pygame.K_TAB)
        self.assertEqual(self.app.modo, "arbol")
        clic_en_boton(self, self.app, "Comparación")
        self.assertEqual(self.app.modo, "comp")
        clic_en_boton(self, self.app, "Modo manual")
        self.assertEqual(self.app.modo, "manual")

    def test_teclas_del_modo_manual(self):
        app = self.app
        app.cambiar_modo("manual")
        pulsar(app, pygame.K_2)                     # 2 misioneros: inválido
        self.assertEqual(app.manual_invalidos, 1)
        pulsar(app, pygame.K_3)                     # 1 caníbal: válido
        correr(app, 2)
        self.assertEqual(app.manual_estado, P.Estado(3, 2, 0))
        pulsar(app, pygame.K_BACKSPACE)
        self.assertEqual(app.manual_estado, P.ESTADO_INICIAL)
        pulsar(app, pygame.K_p)
        self.assertIn("Pista", app.manual_msg[0])

    def test_teclas_del_arbol(self):
        app = self.app
        app.cambiar_modo("arbol")
        pulsar(app, pygame.K_RIGHT)
        self.assertEqual(app.arbol_paso, 1)
        pulsar(app, pygame.K_END)
        self.assertEqual(app.arbol_paso, len(app.resultado().traza))
        pulsar(app, pygame.K_a)
        self.assertEqual(app.algoritmo, "astar")
        self.assertEqual(app.arbol_paso, 0)

    def test_salir(self):
        self.app.manejar_evento(pygame.event.Event(pygame.QUIT))
        self.assertFalse(self.app.corriendo)
