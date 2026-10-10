"""Prototipo gráfico (Pygame) del problema de los Misioneros y los Caníbales.

Pestañas:
  * Simulación       -> resuelve con BFS o A* y anima la ruta solución.
  * Proceso / Árbol  -> muestra paso a paso cómo se construye el árbol de búsqueda.
  * Comparación      -> métricas y parámetros de evaluación de BFS vs A*.
  * Modo manual      -> el usuario juega; se validan los movimientos.

Atajos: Tab cambia de pestaña, Espacio reproduce/pausa, ← → retrocede/avanza,
Inicio/Fin, B = BFS, A = A*, H = heurística, R = resolver, F12 = captura,
1-5 = movimientos en modo manual, Retroceso = deshacer, P = pista, Esc = salir.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

import problema as P  # noqa: E402
from busqueda import (INVALIDO, NUEVO, OBJETIVO, REPETIDO,  # noqa: E402
                      ResultadoBusqueda, a_estrella, bfs)
from metricas import EVALUACION_TEORICA, medir_tiempo, tabla_metricas  # noqa: E402
from problema import Estado  # noqa: E402

ANCHO, ALTO = 1280, 800
FPS = 60

COL = {
    "fondo": (235, 239, 245), "panel": (255, 255, 255), "borde": (203, 213, 225),
    "texto": (30, 41, 59), "suave": (100, 116, 139), "acento": (37, 99, 235),
    "astar": (234, 88, 12), "ok": (22, 163, 74), "error": (220, 38, 38),
    "repetido": (148, 163, 184), "meta": (202, 138, 4), "boton": (241, 245, 249),
    "boton_hover": (226, 232, 240), "barra": (30, 41, 59), "barra2": (51, 65, 85),
    "cielo1": (147, 207, 245), "cielo2": (224, 242, 254), "agua": (37, 125, 205),
    "agua2": (125, 190, 240), "pasto": (110, 170, 40), "pasto2": (77, 124, 15),
    "tierra": (146, 104, 60), "madera": (110, 66, 30), "madera2": (160, 100, 50),
    "piel": (240, 200, 160), "misionero": (37, 56, 140), "canibal": (200, 55, 35),
}
COLOR_TIPO = {NUEVO: COL["ok"], REPETIDO: COL["repetido"],
              INVALIDO: COL["error"], OBJETIVO: COL["meta"]}
NOMBRE_TIPO = {NUEVO: "nuevo", REPETIDO: "repetido", INVALIDO: "inválido", OBJETIVO: "OBJETIVO"}

DESCRIPCION = {
    "bfs": ["Búsqueda no informada.",
            "Frontera FIFO: expande por niveles.",
            "Óptima: menor número de cruces."],
    "astar": ["Búsqueda informada: f(n) = g(n) + h(n).",
              "Frontera = cola de prioridad por f.",
              "g = cruces hechos, h = estimación."],
}
NOMBRE_H = {"cruces": "cruces mínimos (admisible)", "personas": "personas M+C (README)"}


def ruta_base() -> str:
    if getattr(sys, "frozen", False):  # ejecutable generado con PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def personas(m: int, c: int) -> str:
    return (f"{m} misionero{'' if m == 1 else 's'}, "
            f"{c} caníbal{'' if c == 1 else 'es'}")


def compacto(e: Estado) -> str:
    return f"({e.m},{e.c},{e.b})"


def suavizar(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------------------
# Utilidades de dibujo
# ---------------------------------------------------------------------------

class Fuentes:
    def __init__(self) -> None:
        nombres = "segoeui,arial,dejavusans,liberationsans,freesans"
        normal = pygame.font.match_font(nombres)
        negrita = pygame.font.match_font(nombres, bold=True)

        def f(tam: int, bold: bool = False) -> pygame.font.Font:
            ruta = negrita if bold else normal
            fuente = pygame.font.Font(ruta, tam)
            if bold and ruta in (None, normal):
                fuente.set_bold(True)
            return fuente

        self.titulo = f(24, True)
        self.grande = f(34, True)
        self.h2 = f(17, True)
        self.normal = f(16)
        self.negrita = f(15, True)
        self.peq = f(14)
        self.peq_b = f(14, True)
        self.mini = f(12)


def texto(surf, s, fuente, color, pos, ancla="topleft") -> pygame.Rect:
    img = fuente.render(str(s), True, color)
    r = img.get_rect(**{ancla: (int(pos[0]), int(pos[1]))})
    surf.blit(img, r)
    return r


def texto_segmentos(surf, segmentos, pos) -> int:
    """Dibuja [(texto, fuente, color), ...] en una misma línea. Devuelve x final."""
    x, y = pos
    for s, fuente, color in segmentos:
        r = texto(surf, s, fuente, color, (x, y))
        x = r.right
    return x


def panel(surf, rect, fuentes=None, titulo=None) -> pygame.Rect:
    rect = pygame.Rect(rect)
    pygame.draw.rect(surf, COL["panel"], rect, border_radius=10)
    pygame.draw.rect(surf, COL["borde"], rect, 1, border_radius=10)
    if titulo and fuentes:
        texto(surf, titulo, fuentes.h2, COL["texto"], (rect.x + 14, rect.y + 10))
    return rect


class Boton:
    def __init__(self, rect, etiqueta, accion, seleccionado=None, habilitado=None,
                 color=None, oscuro=False):
        self.rect = pygame.Rect(rect)
        self.etiqueta = etiqueta
        self.accion = accion
        self.seleccionado = seleccionado or (lambda: False)
        self.habilitado = habilitado or (lambda: True)
        self.color = color or COL["acento"]
        self.oscuro = oscuro

    def dibujar(self, surf, fuente, mouse) -> None:
        hab, sel = self.habilitado(), self.seleccionado()
        hover = hab and self.rect.collidepoint(mouse)
        if sel:
            fondo, borde, color_txt = self.color, self.color, (255, 255, 255)
        elif not hab:
            fondo, borde, color_txt = (241, 245, 249), COL["borde"], (175, 185, 200)
        elif self.oscuro:
            fondo = (71, 85, 105) if hover else COL["barra2"]
            borde, color_txt = fondo, (226, 232, 240)
        else:
            fondo = COL["boton_hover"] if hover else COL["boton"]
            borde, color_txt = COL["borde"], COL["texto"]
        pygame.draw.rect(surf, fondo, self.rect, border_radius=8)
        pygame.draw.rect(surf, borde, self.rect, 1, border_radius=8)
        etiqueta = self.etiqueta() if callable(self.etiqueta) else self.etiqueta
        texto(surf, etiqueta, fuente, color_txt, self.rect.center, "center")

    def click(self, pos) -> bool:
        if self.habilitado() and self.rect.collidepoint(pos):
            self.accion()
            return True
        return False


# ---------------------------------------------------------------------------
# Escena: río, orillas, personas y bote
# ---------------------------------------------------------------------------

def dibujar_persona(surf, x, y, tipo, s=1.0) -> None:
    """Dibuja un misionero ('M') o un caníbal ('C') con los pies en (x, y)."""
    x, y = int(x), int(y)
    color = COL["misionero"] if tipo == "M" else COL["canibal"]
    grosor = max(2, int(3 * s))
    pygame.draw.line(surf, (55, 55, 60), (x - 5 * s, y - 14 * s), (x - 6 * s, y), grosor)
    pygame.draw.line(surf, (55, 55, 60), (x + 5 * s, y - 14 * s), (x + 6 * s, y), grosor)
    cuerpo = pygame.Rect(0, 0, int(24 * s), int(28 * s))
    cuerpo.midbottom = (x, int(y - 11 * s))
    pygame.draw.rect(surf, color, cuerpo, border_radius=int(7 * s))
    cabeza = (x, int(cuerpo.top - 9 * s))
    r = int(9 * s)
    if tipo == "M":
        # cruz blanca en el pecho y capucha
        pygame.draw.line(surf, (255, 255, 255), (x, cuerpo.top + 5 * s), (x, cuerpo.bottom - 5 * s),
                         max(2, int(3 * s)))
        pygame.draw.line(surf, (255, 255, 255), (x - 6 * s, cuerpo.top + 11 * s),
                         (x + 6 * s, cuerpo.top + 11 * s), max(2, int(3 * s)))
        pygame.draw.circle(surf, color, cabeza, r + max(1, int(2 * s)))
        pygame.draw.circle(surf, COL["piel"], (cabeza[0], cabeza[1] + int(1 * s)), r - 1)
    else:
        pygame.draw.circle(surf, (190, 130, 90), cabeza, r)
        # pluma y cinta
        top = cabeza[1] - r
        pygame.draw.polygon(surf, (250, 200, 30), [(x + 1, top + 3), (x + 6 * s, top - 13 * s),
                                                   (x + 9 * s, top + 1)])
        pygame.draw.line(surf, (120, 30, 20), (x - r, cabeza[1] - 3 * s), (x + r, cabeza[1] - 3 * s),
                         max(2, int(3 * s)))
        # hueso en la mano
        hx, hy = cuerpo.right + 2 * s, cuerpo.centery
        pygame.draw.line(surf, (245, 245, 235), (hx, hy - 7 * s), (hx, hy + 7 * s), max(2, int(3 * s)))
    pygame.draw.circle(surf, (60, 50, 45), cabeza, r, 1)
