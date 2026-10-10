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


def dibujar_escena(surf, rect, estado: Estado, fuentes: Fuentes, anim=None,
                   etiqueta_superior: str | None = None, badge: str | None = None) -> None:
    """Dibuja el río con ambas orillas. ``anim`` = dict(desde, hasta, t) durante un cruce."""
    rect = pygame.Rect(rect)
    x0, y0, w, h = rect
    anterior_clip = surf.get_clip()
    surf.set_clip(rect)

    # Cielo degradado
    for i in range(h):
        k = i / h
        c = [int(COL["cielo1"][j] * (1 - k) + COL["cielo2"][j] * k) for j in range(3)]
        pygame.draw.line(surf, c, (x0, y0 + i), (x0 + w, y0 + i))
    pygame.draw.circle(surf, (253, 224, 71), (x0 + w - 70, y0 + 45), 26)
    for cx, cy in ((x0 + 330, y0 + 40), (x0 + 520, y0 + 70)):
        for dx, dy, rr in ((0, 0, 18), (20, -8, 22), (42, 0, 17)):
            pygame.draw.circle(surf, (255, 255, 255), (cx + dx, cy + dy), rr)

    banco_w = int(w * 0.27)
    yb = y0 + int(h * 0.45)            # altura del pasto
    agua_y = y0 + int(h * 0.64)        # nivel del agua
    rio_izq, rio_der = x0 + banco_w, x0 + w - banco_w

    # Río
    pygame.draw.rect(surf, COL["agua"], (rio_izq - 30, yb + 12, rio_der - rio_izq + 60, h))
    fase = (pygame.time.get_ticks() // 60) % 40
    for fila in range(4):
        yy = yb + 35 + fila * 34
        for xx in range(rio_izq - 20 + (fase + fila * 13) % 40, rio_der + 20, 40):
            pygame.draw.arc(surf, COL["agua2"], (xx, yy, 22, 10), 0, 3.14, 2)

    # Orillas
    for lado in (0, 1):
        if lado == 0:
            poly = [(x0, yb), (rio_izq, yb), (rio_izq + 22, y0 + h), (x0, y0 + h)]
            borde = [(rio_izq, yb), (rio_izq + 22, y0 + h)]
        else:
            poly = [(rio_der, yb), (x0 + w, yb), (x0 + w, y0 + h), (rio_der - 22, y0 + h)]
            borde = [(rio_der, yb), (rio_der - 22, y0 + h)]
        pygame.draw.polygon(surf, COL["pasto"], poly)
        pygame.draw.line(surf, COL["tierra"], *borde, 8)
        pygame.draw.line(surf, COL["pasto2"], poly[0], poly[1], 3)
    for tx in (x0 + 18, x0 + w - 18):  # árboles al fondo
        pygame.draw.rect(surf, (120, 80, 40), (tx - 4, yb - 40, 8, 42))
        pygame.draw.circle(surf, (60, 130, 40), (tx, yb - 48), 20)

    # Personas en cada orilla (durante el cruce, quienes van en el bote no están en tierra)
    if anim:
        desde, hasta = anim["desde"], anim["hasta"]
        izq = (min(desde.m, hasta.m), min(desde.c, hasta.c))
        der = (min(desde.derecha[0], hasta.derecha[0]), min(desde.derecha[1], hasta.derecha[1]))
        pasajeros = (abs(desde.m - hasta.m), abs(desde.c - hasta.c))
    else:
        izq, der, pasajeros = (estado.m, estado.c), estado.derecha, (0, 0)

    sep = 62
    for lado, (m, c) in ((0, izq), (1, der)):
        for fila, (n, tipo) in enumerate(((m, "M"), (c, "C"))):
            pies = yb + 62 + fila * 80
            for i in range(n):
                px = x0 + 42 + i * sep if lado == 0 else x0 + w - 42 - i * sep
                dibujar_persona(surf, px, pies, tipo)
        cx = x0 + banco_w // 2 if lado == 0 else x0 + w - banco_w // 2
        nombre = "Orilla izquierda" if lado == 0 else "Orilla derecha"
        caja = pygame.Rect(0, 0, 170, 42)
        caja.midbottom = (cx, yb - 6)
        fondo = pygame.Surface(caja.size, pygame.SRCALPHA)
        fondo.fill((255, 255, 255, 190))
        surf.blit(fondo, caja)
        texto(surf, nombre, fuentes.peq_b, COL["texto"], (cx, caja.y + 3), "midtop")
        texto_segmentos(surf, [(f"{m} M", fuentes.peq_b, COL["misionero"]),
                               ("   ", fuentes.peq, COL["texto"]),
                               (f"{c} C", fuentes.peq_b, COL["canibal"])], (cx - 32, caja.y + 21))

    # Bote
    bw = 150
    muelle_izq, muelle_der = rio_izq + 6, rio_der - 6 - bw
    if anim:
        x_ini = muelle_izq if anim["desde"].b == P.IZQUIERDA else muelle_der
        x_fin = muelle_izq if anim["hasta"].b == P.IZQUIERDA else muelle_der
        bx = x_ini + (x_fin - x_ini) * suavizar(anim["t"])
    else:
        bx = muelle_izq if estado.b == P.IZQUIERDA else muelle_der
    bx = int(bx)
    by = agua_y - 10
    asientos = [bx + 50, bx + 100]
    tipos = ["M"] * pasajeros[0] + ["C"] * pasajeros[1]
    for asiento, tipo in zip(asientos, tipos):
        dibujar_persona(surf, asiento, by + 16, tipo, 0.85)
    casco = [(bx, by), (bx + bw, by), (bx + bw - 18, by + 26), (bx + 18, by + 26)]
    pygame.draw.polygon(surf, COL["madera2"], casco)
    pygame.draw.polygon(surf, COL["madera"], casco, 3)
    pygame.draw.line(surf, COL["madera"], (bx + 10, by + 10), (bx + bw - 10, by + 10), 2)
    pygame.draw.line(surf, COL["madera"], (bx + bw // 2, by - 30), (bx + bw // 2 + 30, by + 30), 4)  # remo
    texto(surf, "bote (cap. 2)", fuentes.mini, (255, 255, 255), (bx + bw // 2, by + 13), "center")

    # Leyenda
    ley = pygame.Rect(x0 + 10, y0 + 10, 210, 34)
    fondo = pygame.Surface(ley.size, pygame.SRCALPHA)
    fondo.fill((255, 255, 255, 200))
    surf.blit(fondo, ley)
    dibujar_persona(surf, ley.x + 16, ley.bottom - 2, "M", 0.55)
    texto(surf, "Misionero", fuentes.peq, COL["texto"], (ley.x + 30, ley.y + 8))
    dibujar_persona(surf, ley.x + 118, ley.bottom - 2, "C", 0.55)
    texto(surf, "Caníbal", fuentes.peq, COL["texto"], (ley.x + 132, ley.y + 8))

    if badge:
        r = texto(surf, badge, fuentes.negrita, (255, 255, 255), (x0 + w - 120, y0 + 14), "midtop")
        pygame.draw.rect(surf, COL["barra"], r.inflate(20, 10), border_radius=8)
        texto(surf, badge, fuentes.negrita, (255, 255, 255), (x0 + w - 120, y0 + 14), "midtop")
    if etiqueta_superior:
        r = fuentes.negrita.size(etiqueta_superior)
        caja = pygame.Rect(0, 0, r[0] + 24, r[1] + 10)
        caja.midtop = (x0 + w // 2, y0 + 108)
        pygame.draw.rect(surf, (255, 255, 255), caja, border_radius=8)
        pygame.draw.rect(surf, COL["borde"], caja, 1, border_radius=8)
        texto(surf, etiqueta_superior, fuentes.negrita, COL["texto"], caja.center, "center")

    if not anim and P.es_objetivo(estado):
        caja = pygame.Rect(0, 0, 380, 46)
        caja.center = (x0 + w // 2, y0 + 82)
        pygame.draw.rect(surf, COL["ok"], caja, border_radius=10)
        texto(surf, "¡Objetivo alcanzado! Todos cruzaron", fuentes.h2, (255, 255, 255),
              caja.center, "center")

    surf.set_clip(anterior_clip)
    pygame.draw.rect(surf, COL["borde"], rect, 1, border_radius=4)


# ---------------------------------------------------------------------------
# Aplicación
# ---------------------------------------------------------------------------

class App:
    MODOS = [("sim", "Simulación"), ("arbol", "Proceso / Árbol"),
             ("comp", "Comparación"), ("manual", "Modo manual")]
    ESCENA = pygame.Rect(20, 70, 840, 330)
    PANEL_RUTA = pygame.Rect(20, 470, 410, 320)
    PANEL_PROCESO = pygame.Rect(440, 470, 420, 320)
    LIENZO_ARBOL = pygame.Rect(20, 70, 840, 665)

    def __init__(self, pantalla: pygame.Surface) -> None:
        self.pantalla = pantalla
        self.f = Fuentes()
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.modo = "sim"
        self.algoritmo = "bfs"
        self.heuristica = "cruces"
        self._cache: dict = {}
        self._tiempos: dict = {}
        self.velocidades = [0.5, 1.0, 2.0, 4.0]
        self.i_vel = 1
        self.anim = None
        self.toast = None
        # Simulación
        self.resuelto = False
        self.paso = 0
        self.reproduciendo = False
        self.espera = 0.0
        self.scroll_proceso = 0
        # Árbol
        self.arbol_paso = 0
        self.arbol_rep = False
        self.arbol_timer = 0.0
        # Manual
        self.reiniciar_manual()
        self._crear_botones()

    # ----------------------------------------------------------------- datos
    @property
    def vel(self) -> float:
        return self.velocidades[self.i_vel]

    def resultado(self, algoritmo: str | None = None) -> ResultadoBusqueda:
        alg = algoritmo or self.algoritmo
        clave = (alg, self.heuristica if alg == "astar" else None)
        if clave not in self._cache:
            if alg == "bfs":
                self._cache[clave] = bfs()
            else:
                self._cache[clave] = a_estrella(heuristica=P.HEURISTICAS[self.heuristica])
        return self._cache[clave]

    def nombre_algoritmo(self, alg: str | None = None) -> str:
        alg = alg or self.algoritmo
        return "BFS (Anchura)" if alg == "bfs" else "A* (A estrella)"

    def ruta(self):
        return self.resultado().ruta if self.resuelto else []

    def n_pasos(self) -> int:
        return max(len(self.ruta()) - 1, 0)

    def estado_sim(self) -> Estado:
        ruta = self.ruta()
        return ruta[self.paso].estado if ruta else P.ESTADO_INICIAL

    # -------------------------------------------------------------- acciones
    def aviso(self, mensaje: str, segundos: float = 2.5) -> None:
        self.toast = [mensaje, segundos]

    def terminar_anim(self) -> None:
        if self.anim:
            fin = self.anim["fin"]
            self.anim = None
            fin()

    def cambiar_modo(self, modo: str) -> None:
        self.terminar_anim()
        self.reproduciendo = self.arbol_rep = False
        self.modo = modo

    def siguiente_modo(self) -> None:
        claves = [m for m, _ in self.MODOS]
        self.cambiar_modo(claves[(claves.index(self.modo) + 1) % len(claves)])

    def seleccionar_algoritmo(self, alg: str) -> None:
        self.terminar_anim()
        self.algoritmo = alg
        self.reiniciar_sim()
        self.arbol_paso = 0
        self.arbol_rep = False

    def alternar_heuristica(self) -> None:
        self.heuristica = "personas" if self.heuristica == "cruces" else "cruces"
        if self.algoritmo == "astar":
            self.seleccionar_algoritmo("astar")
        self.aviso(f"Heurística de A*: {NOMBRE_H[self.heuristica]}")

    def reiniciar_sim(self) -> None:
        self.resuelto = False
        self.paso = 0
        self.reproduciendo = False
        self.scroll_proceso = 0

    def resolver(self) -> None:
        self.terminar_anim()
        r = self.resultado()
        self.resuelto = True
        self.paso = 0
        self.reproduciendo = False
        self.scroll_proceso = 0
        self.aviso(f"{r.algoritmo}: solución de {r.longitud} cruces, "
                   f"{r.nodos_expandidos} nodos expandidos")

    def iniciar_anim(self, desde: Estado, hasta: Estado, fin) -> None:
        self.anim = {"desde": desde, "hasta": hasta, "t": 0.0, "dur": 1.2 / self.vel, "fin": fin}

    def avanzar(self) -> None:
        if self.anim or not self.resuelto or self.paso >= self.n_pasos():
            return
        ruta = self.ruta()

        def fin():
            self.paso += 1
        self.iniciar_anim(ruta[self.paso].estado, ruta[self.paso + 1].estado, fin)

    def retroceder(self) -> None:
        self.reproduciendo = False
        if self.anim:
            self.anim = None
        elif self.paso > 0:
            self.paso -= 1

    def ir_inicio(self) -> None:
        self.anim = None
        self.reproduciendo = False
        self.paso = 0

    def ir_final(self) -> None:
        self.anim = None
        self.reproduciendo = False
        self.paso = self.n_pasos()

    def alternar_reproduccion(self) -> None:
        if self.modo == "arbol":
            if self.arbol_paso >= len(self.resultado().traza):
                self.arbol_paso = 0
            self.arbol_rep = not self.arbol_rep
            return
        if not self.resuelto:
            self.resolver()
        if self.paso >= self.n_pasos():
            self.paso = 0
        self.reproduciendo = not self.reproduciendo
        self.espera = 1.0

    def cambiar_velocidad(self) -> None:
        self.i_vel = (self.i_vel + 1) % len(self.velocidades)

    # árbol
    def arbol_mover(self, delta: int | None = None, absoluto: int | None = None) -> None:
        total = len(self.resultado().traza)
        self.arbol_rep = False
        valor = absoluto if absoluto is not None else self.arbol_paso + (delta or 0)
        self.arbol_paso = max(0, min(total, valor))

    def arbol_final(self) -> None:
        self.arbol_mover(absoluto=len(self.resultado().traza))

    # manual
    def reiniciar_manual(self) -> None:
        self.anim = None
        self.manual_estado = P.ESTADO_INICIAL
        self.manual_hist: list[tuple[Estado, tuple[int, int]]] = []
        self.manual_invalidos = 0
        self.manual_msg = ("Elige quién cruza en el bote (teclas 1-5).", COL["suave"])

    def mover_manual(self, accion: tuple[int, int]) -> None:
        if self.anim:
            return
        e = self.manual_estado
        if P.es_objetivo(e):
            self.manual_msg = ("Ya resolviste el problema. Pulsa «Reiniciar».", COL["ok"])
            return
        nuevo = P.aplicar(e, accion)
        motivo = P.motivo_invalidez(nuevo)
        if motivo:
            self.manual_invalidos += 1
            self.manual_msg = (f"Movimiento inválido ({P.nombre_accion(accion)} → {nuevo}): {motivo}",
                               COL["error"])
            return
        visitados = {estado for estado, _a in self.manual_hist}
        repetido = nuevo in visitados

        def fin():
            self.manual_estado = nuevo
            self.manual_hist.append((e, accion))
            if P.es_objetivo(nuevo):
                self.manual_msg = (f"¡Lo lograste en {len(self.manual_hist)} cruces! "
                                   f"(el óptimo es 11)", COL["ok"])
            elif repetido:
                self.manual_msg = (f"Estado {nuevo} repetido: volviste a un estado anterior (ciclo).",
                                   COL["meta"])
            else:
                self.manual_msg = (f"{P.describir_movimiento(accion, e)} → {nuevo}", COL["texto"])
        self.manual_msg = (P.describir_movimiento(accion, e) + "...", COL["texto"])
        self.iniciar_anim(e, nuevo, fin)

    def deshacer_manual(self) -> None:
        if self.anim or not self.manual_hist:
            return
        self.manual_estado, accion = self.manual_hist.pop()
        self.manual_msg = (f"Se deshizo el movimiento {P.nombre_accion(accion)}.", COL["suave"])

    def pista(self) -> None:
        if self.anim:
            return
        r = bfs(self.manual_estado)
        if not r.encontrada:
            self.manual_msg = ("No hay solución desde este estado.", COL["error"])
        elif r.longitud == 0:
            self.manual_msg = ("Ya estás en el estado objetivo.", COL["ok"])
        else:
            accion = r.ruta[1].accion
            self.manual_msg = (f"Pista (BFS): {P.describir_movimiento(accion, self.manual_estado)}"
                               f" — faltan {r.longitud} cruces como mínimo.", COL["acento"])

    def captura(self, nombre: str | None = None) -> str:
        carpeta = os.path.join(ruta_base(), "capturas")
        os.makedirs(carpeta, exist_ok=True)
        nombre = nombre or f"captura_{self.modo}_{datetime.now():%Y%m%d_%H%M%S}.png"
        ruta = os.path.join(carpeta, nombre)
        pygame.image.save(self.pantalla, ruta)
        self.aviso(f"Captura guardada: capturas/{nombre}")
        return ruta

    # --------------------------------------------------------------- botones
    def _crear_botones(self) -> None:
        superior = []
        for i, (clave, nombre) in enumerate(self.MODOS):
            superior.append(Boton((470 + i * 152, 10, 145, 36), nombre,
                                  lambda c=clave: self.cambiar_modo(c),
                                  seleccionado=lambda c=clave: self.modo == c, oscuro=True))

        metodo = [
            Boton((895, 106, 110, 34), "BFS", lambda: self.seleccionar_algoritmo("bfs"),
                  seleccionado=lambda: self.algoritmo == "bfs"),
            Boton((1015, 106, 110, 34), "A*", lambda: self.seleccionar_algoritmo("astar"),
                  seleccionado=lambda: self.algoritmo == "astar", color=COL["astar"]),
            Boton((1135, 106, 110, 34), "Captura", lambda: self.captura()),
            Boton((895, 148, 350, 30), lambda: f"h(n) de A*: {NOMBRE_H[self.heuristica]}",
                  self.alternar_heuristica),
        ]
        resuelto = lambda: self.resuelto  # noqa: E731
        y = 412
        controles_sim = [
            Boton((20, y, 100, 42), "Resolver", self.resolver, color=COL["ok"],
                  seleccionado=lambda: not self.resuelto),
            Boton((128, y, 70, 42), "Inicio", self.ir_inicio, habilitado=resuelto),
            Boton((206, y, 88, 42), "Anterior", self.retroceder, habilitado=resuelto),
            Boton((302, y, 110, 42), lambda: "Pausa" if self.reproduciendo else "Reproducir",
                  self.alternar_reproduccion, seleccionado=lambda: self.reproduciendo),
            Boton((420, y, 92, 42), "Siguiente", self.avanzar, habilitado=resuelto),
            Boton((520, y, 62, 42), "Final", self.ir_final, habilitado=resuelto),
            Boton((590, y, 125, 42), lambda: f"Velocidad: {self.vel:g}x", self.cambiar_velocidad),
        ]
        y = 745
        controles_arbol = [
            Boton((20, y, 80, 42), "Inicio", lambda: self.arbol_mover(absoluto=0)),
            Boton((108, y, 95, 42), "Anterior", lambda: self.arbol_mover(-1)),
            Boton((211, y, 120, 42), lambda: "Pausa" if self.arbol_rep else "Reproducir",
                  self.alternar_reproduccion, seleccionado=lambda: self.arbol_rep),
            Boton((339, y, 100, 42), "Siguiente", lambda: self.arbol_mover(1)),
            Boton((447, y, 70, 42), "Final", self.arbol_final),
            Boton((525, y, 135, 42), lambda: f"Velocidad: {self.vel:g}x", self.cambiar_velocidad),
        ]
        comp = [
            Boton((900, 78, 220, 30), lambda: f"h(n): {self.heuristica}", self.alternar_heuristica),
            Boton((1130, 78, 120, 30), "Captura", lambda: self.captura()),
        ]
        y = 412
        acciones = [((1, 0), "1 Misionero", 130), ((2, 0), "2 Misioneros", 140),
                    ((0, 1), "1 Caníbal", 120), ((0, 2), "2 Caníbales", 130), ((1, 1), "1M + 1C", 100)]
        manual = []
        x = 20
        for accion, nombre, ancho in acciones:
            manual.append(Boton((x, y, ancho, 42), nombre, lambda a=accion: self.mover_manual(a)))
            x += ancho + 8
        manual += [
            Boton((x, y, 95, 42), "Deshacer", self.deshacer_manual,
                  habilitado=lambda: bool(self.manual_hist)),
            Boton((880, 745, 120, 42), "Pista (BFS)", self.pista, color=COL["acento"]),
            Boton((1008, 745, 120, 42), "Reiniciar", self.reiniciar_manual),
            Boton((1136, 745, 124, 42), "Captura", lambda: self.captura()),
        ]
        self.botones = {
            "superior": superior,
            "sim": metodo + controles_sim,
            "arbol": metodo + controles_arbol,
            "comp": comp,
            "manual": manual,
        }

    def botones_activos(self) -> list[Boton]:
        return self.botones["superior"] + self.botones[self.modo]

    # ---------------------------------------------------------------- eventos
    def manejar_evento(self, ev) -> None:
        if ev.type == pygame.QUIT:
            self.corriendo = False
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for b in self.botones_activos():
                if b.click(ev.pos):
                    return
            if self.modo == "sim" and self.resuelto and not self.anim:
                fila = (ev.pos[1] - (self.PANEL_RUTA.y + 44)) // 21
                if self.PANEL_RUTA.collidepoint(ev.pos) and 0 <= fila <= self.n_pasos():
                    self.reproduciendo = False
                    self.paso = fila
        elif ev.type == pygame.MOUSEWHEEL:
            if self.modo == "sim" and self.PANEL_PROCESO.collidepoint(pygame.mouse.get_pos()):
                self.scroll_proceso = max(0, self.scroll_proceso - ev.y * 38)
        elif ev.type == pygame.KEYDOWN:
            self.manejar_tecla(ev.key)

    def manejar_tecla(self, k) -> None:
        if k == pygame.K_ESCAPE:
            self.corriendo = False
        elif k == pygame.K_F12:
            self.captura()
        elif k == pygame.K_TAB:
            self.siguiente_modo()
        elif self.modo in ("sim", "arbol"):
            if k == pygame.K_b:
                self.seleccionar_algoritmo("bfs")
            elif k == pygame.K_a:
                self.seleccionar_algoritmo("astar")
            elif k == pygame.K_h:
                self.alternar_heuristica()
            elif k == pygame.K_SPACE:
                self.alternar_reproduccion()
            elif self.modo == "sim":
                acciones = {pygame.K_r: self.resolver, pygame.K_RIGHT: self.avanzar,
                            pygame.K_LEFT: self.retroceder, pygame.K_HOME: self.ir_inicio,
                            pygame.K_END: self.ir_final}
                if k in acciones:
                    acciones[k]()
            else:
                acciones = {pygame.K_RIGHT: lambda: self.arbol_mover(1),
                            pygame.K_LEFT: lambda: self.arbol_mover(-1),
                            pygame.K_HOME: lambda: self.arbol_mover(absoluto=0),
                            pygame.K_END: self.arbol_final}
                if k in acciones:
                    acciones[k]()
        elif self.modo == "comp" and k == pygame.K_h:
            self.alternar_heuristica()
        elif self.modo == "manual":
            teclas = {pygame.K_1: (1, 0), pygame.K_2: (2, 0), pygame.K_3: (0, 1),
                      pygame.K_4: (0, 2), pygame.K_5: (1, 1)}
            if k in teclas:
                self.mover_manual(teclas[k])
            elif k == pygame.K_BACKSPACE:
                self.deshacer_manual()
            elif k == pygame.K_p:
                self.pista()

    def actualizar(self, dt: float) -> None:
        if self.anim:
            self.anim["t"] += dt / self.anim["dur"]
            if self.anim["t"] >= 1:
                self.terminar_anim()
        if self.modo == "sim" and self.reproduciendo and not self.anim:
            if self.paso >= self.n_pasos():
                self.reproduciendo = False
            else:
                self.espera += dt
                if self.espera >= 0.35 / self.vel:
                    self.espera = 0.0
                    self.avanzar()
        if self.modo == "arbol" and self.arbol_rep:
            self.arbol_timer += dt
            if self.arbol_timer >= 0.8 / self.vel:
                self.arbol_timer = 0.0
                if self.arbol_paso < len(self.resultado().traza):
                    self.arbol_paso += 1
                else:
                    self.arbol_rep = False
        if self.toast:
            self.toast[1] -= dt
            if self.toast[1] <= 0:
                self.toast = None

    # ---------------------------------------------------------------- dibujo
    def dibujar(self) -> None:
        s = self.pantalla
        s.fill(COL["fondo"])
        pygame.draw.rect(s, COL["barra"], (0, 0, ANCHO, 56))
        texto(s, "Misioneros y Caníbales", self.f.titulo, (255, 255, 255), (20, 6))
        texto(s, "Búsqueda en Anchura (BFS) vs A*  ·  Inteligencia Artificial UMSS 2026",
              self.f.mini, (148, 163, 184), (22, 36))
        getattr(self, f"dibujar_{self.modo}")()
        mouse = pygame.mouse.get_pos()
        for b in self.botones_activos():
            fuente = self.f.negrita if b in self.botones["superior"] else self.f.peq_b
            b.dibujar(s, fuente, mouse)
        if self.toast:
            img = self.f.negrita.render(self.toast[0], True, (255, 255, 255))
            r = img.get_rect(midbottom=(ANCHO // 2, ALTO - 16))
            pygame.draw.rect(s, (15, 23, 42), r.inflate(28, 16), border_radius=10)
            s.blit(img, r)

    # -- tarjetas comunes
    def dibujar_metodologia(self) -> None:
        r = panel(self.pantalla, (880, 70, 380, 190), self.f, "Metodología de búsqueda")
        color = COL["acento"] if self.algoritmo == "bfs" else COL["astar"]
        y = r.y + 116
        texto(self.pantalla, self.nombre_algoritmo(), self.f.negrita, color, (r.x + 15, y))
        for i, linea in enumerate(DESCRIPCION[self.algoritmo]):
            texto(self.pantalla, linea, self.f.peq, COL["suave"], (r.x + 15, y + 20 + i * 17))

    def dibujar_estado(self, rect, estado: Estado, paso_txt: str, mov_txt: str) -> None:
        s = self.pantalla
        r = panel(s, rect, self.f, "Estado actual  (M, C, B)")
        texto(s, str(estado), self.f.grande, COL["texto"], (r.centerx, r.y + 36), "midtop")
        m_der, c_der = estado.derecha
        filas = [
            ("Orilla izquierda:", personas(estado.m, estado.c)),
            ("Orilla derecha:", personas(m_der, c_der)),
            ("Bote:", "orilla izquierda" if estado.b == P.IZQUIERDA else "orilla derecha"),
            ("Paso:", paso_txt),
            ("Movimiento:", mov_txt),
            ("Test objetivo:", "Sí, estado objetivo" if P.es_objetivo(estado) else "No"),
        ]
        for i, (k, v) in enumerate(filas):
            y = r.y + 86 + i * 20
            texto(s, k, self.f.peq_b, COL["suave"], (r.x + 15, y))
            color = COL["ok"] if k == "Test objetivo:" and P.es_objetivo(estado) else COL["texto"]
            texto(s, v, self.f.peq, color, (r.x + 125, y))

    # -- simulación
    def dibujar_sim(self) -> None:
        s = self.pantalla
        ruta = self.ruta()
        estado = self.estado_sim()
        etiqueta = None
        if self.anim:
            etiqueta = P.describir_movimiento(ruta[self.paso + 1].accion, ruta[self.paso].estado)
        elif self.resuelto and self.paso > 0:
            nodo = ruta[self.paso]
            etiqueta = f"Paso {self.paso}: {P.describir_movimiento(nodo.accion, nodo.padre.estado)}"
        badge = "BFS" if self.algoritmo == "bfs" else "A*"
        dibujar_escena(s, self.ESCENA, estado, self.f, self.anim, etiqueta, badge)
        if self.resuelto:
            txt = f"Paso {self.paso} de {self.n_pasos()}"
        else:
            txt = "Pulsa «Resolver»"
        texto(s, txt, self.f.negrita, COL["texto"], (855, 433), "midright")

        self.dibujar_metodologia()
        if self.anim:
            mov = P.nombre_accion(ruta[self.paso + 1].accion) + " (cruzando...)"
        elif self.resuelto and self.paso > 0:
            nodo = ruta[self.paso]
            dirc = "izq → der" if nodo.padre.estado.b == P.IZQUIERDA else "der → izq"
            mov = f"{P.nombre_accion(nodo.accion)}  ({dirc})"
        else:
            mov = "— (estado inicial)"
        paso_txt = f"{self.paso} / {self.n_pasos()}" if self.resuelto else "—"
        self.dibujar_estado((880, 270, 380, 215), estado, paso_txt, mov)

        r = panel(s, (880, 495, 380, 295), self.f, "Métricas de la búsqueda")
        if not self.resuelto:
            texto(s, "Aún no se ejecutó la búsqueda.", self.f.peq, COL["suave"], (r.x + 15, r.y + 44))
        else:
            for i, (k, v) in enumerate(tabla_metricas(self.resultado())):
                y = r.y + 40 + i * 22
                if i % 2 == 0:
                    pygame.draw.rect(s, (248, 250, 252), (r.x + 8, y - 2, r.w - 16, 22))
                texto(s, k, self.f.peq, COL["texto"], (r.x + 15, y))
                texto(s, v, self.f.peq_b, COL["texto"], (r.right - 15, y), "topright")

        self.dibujar_panel_ruta()
        self.dibujar_panel_proceso()

    def dibujar_panel_ruta(self) -> None:
        s = self.pantalla
        r = panel(s, self.PANEL_RUTA, self.f, "Ruta solución")
        if not self.resuelto:
            texto(s, "Sin resolver.", self.f.peq, COL["suave"], (r.x + 15, r.y + 44))
            return
        res = self.resultado()
        texto(s, f"{res.longitud} cruces · costo {res.costo}", self.f.peq, COL["suave"],
              (r.right - 14, r.y + 13), "topright")
        for i, nodo in enumerate(res.ruta):
            y = r.y + 44 + i * 21
            if i == self.paso:
                pygame.draw.rect(s, (219, 234, 254), (r.x + 8, y - 2, r.w - 16, 21), border_radius=5)
            color = COL["texto"] if i <= self.paso else COL["suave"]
            texto(s, f"{i:>2}", self.f.peq_b, color, (r.x + 30, y), "topright")
            texto(s, compacto(nodo.estado), self.f.peq_b, color, (r.x + 42, y))
            if nodo.padre is None:
                texto(s, "estado inicial", self.f.peq, color, (r.x + 120, y))
            else:
                dirc = "izq → der" if nodo.padre.estado.b == P.IZQUIERDA else "der → izq"
                texto(s, P.nombre_accion(nodo.accion), self.f.peq, color, (r.x + 120, y))
                texto(s, dirc, self.f.peq, color, (r.x + 190, y))
            if P.es_objetivo(nodo.estado):
                texto(s, "META", self.f.peq_b, COL["ok"], (r.right - 16, y), "topright")

    def dibujar_panel_proceso(self) -> None:
        s = self.pantalla
        r = panel(s, self.PANEL_PROCESO, self.f, "Proceso de búsqueda")
        x = r.right - 14
        for tipo in (OBJETIVO, INVALIDO, REPETIDO, NUEVO):
            img = self.f.mini.render(NOMBRE_TIPO[tipo], True, COLOR_TIPO[tipo])
            x -= img.get_width()
            s.blit(img, (x, r.y + 15))
            x -= 10
        if not self.resuelto:
            texto(s, "Sin resolver.", self.f.peq, COL["suave"], (r.x + 15, r.y + 44))
            return
        res = self.resultado()
        lineas = self.lineas_proceso(res)
        area = pygame.Rect(r.x + 8, r.y + 40, r.w - 16, r.h - 48)
        alto_total = len(lineas) * 19
        self.scroll_proceso = min(self.scroll_proceso, max(0, alto_total - area.h))
        clip = s.get_clip()
        s.set_clip(area)
        for i, segs in enumerate(lineas):
            y = area.y + i * 19 - self.scroll_proceso
            if area.y - 19 < y < area.bottom:
                texto_segmentos(s, segs, (area.x + 6, y))
        s.set_clip(clip)
        if alto_total > area.h:
            barra_h = max(20, area.h * area.h // alto_total)
            barra_y = area.y + (area.h - barra_h) * self.scroll_proceso // max(1, alto_total - area.h)
            pygame.draw.rect(s, COL["borde"], (r.right - 8, barra_y, 4, barra_h), border_radius=2)

    def lineas_proceso(self, res: ResultadoBusqueda) -> list:
        f = self.f
        es_a = res.algoritmo.startswith("A*")
        lineas = []
        for paso in res.traza:
            n = paso.nodo
            valores = f"g={n.g} h={n.h} f={n.f}" if es_a else f"g={n.g}"
            if paso.es_meta:
                lineas.append([(f"#{paso.numero} ", f.peq_b, COL["meta"]),
                               (f"Selecciona {compacto(n.estado)} {valores} → OBJETIVO", f.peq_b,
                                COL["meta"])])
                lineas.append([("    test objetivo al extraer de la frontera", f.mini, COL["suave"])])
                continue
            lineas.append([(f"#{paso.numero} ", f.peq_b, COL["acento"]),
                           (f"Expande {compacto(n.estado)}  ", f.peq_b, COL["texto"]),
                           (valores, f.peq, COL["suave"])])
            segs = [("    ", f.peq, COL["texto"])]
            invalidos = 0
            for suc in paso.sucesores:
                if suc.tipo == INVALIDO:
                    invalidos += 1
                    continue
                segs.append((f"{P.nombre_accion(suc.accion)}→{compacto(suc.estado)}  ", f.peq,
                             COLOR_TIPO[suc.tipo]))
            if invalidos:
                segs.append((f"+{invalidos} inválidos", f.peq, COL["error"]))
            lineas.append(segs)
            frontera = " ".join(compacto(e) for e, _g, _h in paso.frontera) or "vacía"
            if len(frontera) > 52:
                frontera = frontera[:50] + "…"
            lineas.append([("    Frontera: ", f.mini, COL["suave"]), (frontera, f.mini, COL["suave"])])
        return lineas
