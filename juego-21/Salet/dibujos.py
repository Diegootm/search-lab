"""
dibujos.py - Dibujos del juego con pygame: colores, textos, dados, sombras,
cubilete y decoración del menú. No contiene reglas ni lógica de la partida.
"""
import math

import pygame

# ---------------------------------------------------------------
# Tamaño de pantalla y colores
# ---------------------------------------------------------------
ANCHO, ALTO = 1100, 700
CX = 550                              # centro horizontal de la mesa
FONDO = (14, 22, 28)
PANEL = (22, 34, 42)
PANO = (14, 88, 64)                   # paño verde de la mesa
PANO_OSC = (9, 62, 45)
MADERA = (112, 72, 42)
ORO = (236, 190, 100)
AZUL = (110, 176, 240)
BLANCO = (242, 240, 232)
GRIS = (150, 168, 168)
VERDE = (120, 220, 160)
ROJO = (226, 98, 98)
COLOR_JUGADOR = {"A": ORO, "B": AZUL}
COLOR_MINIMAX = (255, 150, 120)       # coral
COLOR_ALFABETA = (190, 150, 255)      # violeta


# ---------------------------------------------------------------
# Texto y utilidades de dibujo
# ---------------------------------------------------------------
_fuentes = {}


def fuente(tam, negrita=False, titulo=False):
    clave = (tam, negrita, titulo)
    if clave not in _fuentes:
        nombres = ("bahnschrift,impact,segoeuib,arial" if titulo
                   else "segoeui,arial,helvetica,dejavusans")
        _fuentes[clave] = pygame.font.SysFont(nombres, tam, bold=negrita)
    return _fuentes[clave]


def texto(sup, s, tam, color, pos, ancla="topleft", negrita=False, titulo=False):
    """Dibuja texto y devuelve su rectángulo."""
    img = fuente(tam, negrita, titulo).render(s, True, color)
    r = img.get_rect(**{ancla: pos})
    sup.blit(img, r)
    return r


def aclarar(color, n=28):
    return tuple(min(255, c + n) for c in color)


def suave(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def rombo(sup, cx, cy, r, color, grosor=0):
    pygame.draw.polygon(sup, color, [(cx, cy - r), (cx + r, cy),
                                     (cx, cy + r), (cx - r, cy)], grosor)


def partir_lineas(s, tam, ancho, negrita=False):
    """Parte un texto largo en líneas que quepan en 'ancho' píxeles."""
    f = fuente(tam, negrita)
    lineas, actual = [], ""
    for palabra in s.split(" "):
        prueba = (actual + " " + palabra).strip()
        if actual and f.size(prueba)[0] > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = prueba
    if actual:
        lineas.append(actual)
    return lineas


# ---------------------------------------------------------------
# Dados y sombras
# ---------------------------------------------------------------
PIPS = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)],
        4: [(0, 0), (2, 0), (0, 2), (2, 2)],
        5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
        6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}


def dibujar_dado(sup, cx, cy, tam, cara, angulo=0.0):
    """Dibuja un dado con su cara (1..6), opcionalmente girado."""
    s = pygame.Surface((tam, tam), pygame.SRCALPHA)
    radio = tam // 5
    pygame.draw.rect(s, (250, 248, 240), (0, 0, tam, tam), border_radius=radio)
    pygame.draw.rect(s, (176, 172, 160), (0, 0, tam, tam),
                     width=max(2, tam // 22), border_radius=radio)
    margen = tam * 0.27
    paso = (tam - 2 * margen) / 2
    for i, j in PIPS[cara]:
        centro = (int(margen + i * paso), int(margen + j * paso))
        pygame.draw.circle(s, (30, 30, 36), centro, max(3, tam // 10))
    if angulo:
        s = pygame.transform.rotozoom(s, angulo, 1.0)
    sup.blit(s, s.get_rect(center=(int(cx), int(cy))))


def dibujar_sombra(sup, cx, cy, ancho, alfa):
    s = pygame.Surface((ancho, int(ancho * 0.34)), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, alfa), (0, 0, s.get_width(), s.get_height()))
    sup.blit(s, s.get_rect(center=(int(cx), int(cy))))


# ---------------------------------------------------------------
# Cubilete y su movimiento
# ---------------------------------------------------------------
_cubilete = None


def superficie_cubilete():
    """Dibuja el cubilete una sola vez y lo reutiliza."""
    global _cubilete
    if _cubilete is None:
        w, h = 190, 220
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2
        sup_ancho, inf_ancho = 128, 88
        arriba, abajo = 44, 196
        cuerpo = [(cx - sup_ancho // 2, arriba), (cx + sup_ancho // 2, arriba),
                  (cx + inf_ancho // 2, abajo), (cx - inf_ancho // 2, abajo)]
        pygame.draw.polygon(s, (146, 94, 56), cuerpo)
        pygame.draw.polygon(s, (172, 116, 72),
                            [(cx - 42, arriba), (cx - 14, arriba),
                             (cx - 9, abajo), (cx - 28, abajo)])
        for y in (76, 166):
            frac = (y - arriba) / (abajo - arriba)
            ancho = sup_ancho - (sup_ancho - inf_ancho) * frac
            pygame.draw.line(s, ORO, (int(cx - ancho / 2 + 2), y),
                             (int(cx + ancho / 2 - 2), y), 4)
        pygame.draw.ellipse(s, (146, 94, 56),
                            (cx - inf_ancho // 2, abajo - 12, inf_ancho, 24))
        pygame.draw.ellipse(s, (52, 30, 18),
                            (cx - sup_ancho // 2, arriba - 15, sup_ancho, 30))
        pygame.draw.ellipse(s, ORO,
                            (cx - sup_ancho // 2, arriba - 15, sup_ancho, 30), 3)
        texto(s, "21", 34, ORO, (cx, 122), "center", True)
        _cubilete = s
    return _cubilete


def pose_cubilete(t):
    """Posición (x, y, ángulo) del cubilete según el tiempo de la animación."""
    if t < 0.8:                                   # se agita
        amp = min(1.0, (0.8 - t) / 0.1)
        return (CX + math.sin(t * 38) * 11 * amp,
                214 + abs(math.sin(t * 19)) * 7 * amp,
                math.sin(t * 38) * 5 * amp)
    if t < 1.1:                                   # se inclina y suelta los dados
        k = suave((t - 0.8) / 0.3)
        return CX + 105 * k, 214 - 26 * k, -62 * k
    if t < 1.7:
        return CX + 105, 188, -62
    k = suave((t - 1.7) / 0.4)                    # vuelve a su sitio
    return CX + 105 * (1 - k), 188 + 26 * k, -62 * (1 - k)


_fondo_menu = None


def superficie_fondo_menu():
    """Sala de juego oscura con mesa, dados, cubilete y vela. Se dibuja una vez."""
    global _fondo_menu
    if _fondo_menu is not None:
        return _fondo_menu
    s = pygame.Surface((ANCHO, ALTO))
    for y in range(ALTO):                               
        k = y / ALTO
        pygame.draw.line(s, (int(9 + 18 * k), int(12 + 7 * k), int(19 - 3 * k)),
                         (0, y), (ANCHO, y))
    luz = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)  
    for i in range(18):
        w, h = 1000 - i * 48, 760 - i * 36
        pygame.draw.ellipse(luz, (215, 150, 70, 3 + i * 2),
                            (CX - w // 2, 330 - h // 2, w, h))
    s.blit(luz, (0, 0))
    pygame.draw.rect(s, (46, 20, 20), (0, 640, ANCHO, ALTO - 640))
    pygame.draw.rect(s, (96, 50, 34), (0, 640, ANCHO, 4))
    pygame.draw.line(s, (150, 112, 60), (0, 666), (ANCHO, 666), 2)
    pygame.draw.line(s, (150, 112, 60), (0, 674), (ANCHO, 674), 1)
    for x, y, ang in ((176, 668, 14), (244, 662, -20)):
        dibujar_sombra(s, x + 4, y + 30, 56, 110)
        dibujar_dado(s, x, y, 52, 4 if x < 200 else 6, ang)
    cub = pygame.transform.rotozoom(superficie_cubilete(), 0, 0.62)
    dibujar_sombra(s, 940, 660, 96, 110)
    s.blit(cub, cub.get_rect(center=(940, 592)))
    halo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    for i in range(12):
        r = 110 - i * 8
        pygame.draw.circle(halo, (255, 190, 90, 5 + i * 2), (88, 566), r)
    s.blit(halo, (0, 0))
    pygame.draw.rect(s, (226, 214, 184), (77, 580, 22, 68), border_radius=3)
    pygame.draw.ellipse(s, (255, 190, 80), (82, 552, 12, 26))
    pygame.draw.ellipse(s, (255, 236, 170), (85, 560, 6, 14))
    _fondo_menu = s
    return s
