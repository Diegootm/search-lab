"""
interfaz.py - Juego 21 con interfaz gráfica (pygame).

Ejecutar:   python interfaz.py

Este archivo maneja la ventana, los menús, los botones y los eventos.
Los dibujos están en dibujos.py, la IA en ia.py y las reglas en reglas.py.

Controles (también se puede usar el mouse):
  ESPACIO / ENTER = lanzar los dados   P = plantarse   R = relanzar   ESC = menú
"""
import math
import random
import sys
import threading

import pygame

import reglas
from reglas import RESULTADOS, valor, nombre, utilidad
from dibujos import (
    ALTO, ANCHO, AZUL, BLANCO, COLOR_ALFABETA, COLOR_JUGADOR, COLOR_MINIMAX,
    CX, FONDO, GRIS, MADERA, ORO, PANEL, PANO, PANO_OSC, ROJO, VERDE,
    aclarar, dibujar_dado, dibujar_sombra, partir_lineas, pose_cubilete,
    rombo, suave, superficie_cubilete, superficie_fondo_menu, texto,
)
from ia import mejor_accion, comparar_desde_inicio

FPS = 60

FIN_TARJETA = pygame.Rect(60, 52, 980, 600)   
AYUDA_TARJETA = pygame.Rect(120, 50, 860, 600)  

NOMBRE_METODO = {"minimax": "Minimax", "alfabeta": "Alfa-Beta"}

DURACION_LANZ = 2.1
T_SALEN_DADOS = 0.95                  
DADO_TAM = 84
POS_DADOS = [(CX - 64, 392), (CX + 64, 392)]


def fmt_tiempo(seg):
    """Tiempo legible: milisegundos si es corto, segundos si es largo."""
    if seg >= 1.0:
        return f"{seg:.2f} s"
    return f"{seg * 1000:.1f} ms"


def armar_filas(um, ua, igual, nm, na, pm, pa, tm, ta):
    """
    Filas de una tabla de comparación: (etiqueta, minimax, alfabeta, mejor).
    'mejor' indica qué columna se resalta en verde ('mm', 'ab', 'ambos' o None).
    """
    def menor(a, b):
        return "ab" if b < a else "mm" if a < b else "ambos"
    evitado = f"{100 * (1 - na / nm):.1f} %" if nm else "—"
    return [("Utilidad", um, ua, "ambos" if igual else None),
            ("Nodos", f"{nm:,}", f"{na:,}", menor(nm, na)),
            ("Podas", f"{pm:,}", f"{pa:,}", None),
            ("Tiempo", fmt_tiempo(tm), fmt_tiempo(ta), menor(tm, ta)),
            ("Nodos evitados", "—", evitado, None)]


class Boton:
    def __init__(self, clave, rect, etiqueta, color=ORO, seleccionado=None,
                 tam=24, estilo="caja"):
        self.estilo = estilo                  
        self.clave = clave
        self.rect = rect
        self.etiqueta = etiqueta
        self.color = color
        self.seleccionado = seleccionado      
        self.tam = tam

    def dibujar(self, sup, hover):
        if self.estilo == "texto":
            self.dibujar_texto(sup, hover)
            return
        relleno = self.seleccionado is None or self.seleccionado
        if relleno:
            color = aclarar(self.color) if hover else self.color
            pygame.draw.rect(sup, color, self.rect, border_radius=12)
            texto(sup, self.etiqueta, self.tam, (20, 24, 28),
                  self.rect.center, "center", True)
        else:
            fondo = (36, 52, 62) if hover else (24, 36, 44)
            pygame.draw.rect(sup, fondo, self.rect, border_radius=12)
            pygame.draw.rect(sup, GRIS, self.rect, 2, border_radius=12)
            texto(sup, self.etiqueta, self.tam, BLANCO,
                  self.rect.center, "center", True)


    def dibujar_texto(self, sup, hover):
        """Opción de menú: solo texto dorado; la elegida lleva rombos a los lados."""
        if self.seleccionado is None:                
            color = (255, 226, 150) if hover else ORO
        elif self.seleccionado:                      
            color = (255, 226, 150)
        else:                                        
            color = (236, 205, 140) if hover else (150, 128, 92)
        r = texto(sup, self.etiqueta, self.tam, color, self.rect.center,
                  "center", True, True)
        if self.seleccionado or hover:
            lado = 20 + self.tam // 6
            for cx in (r.left - lado, r.right + lado):
                rombo(sup, cx, r.centery, max(4, self.tam // 5), color)
        if self.seleccionado:
            pygame.draw.line(sup, color, (r.left, r.bottom + 2), (r.right, r.bottom + 2), 2)



class Juego:
    def __init__(self):
        self.fase = "MENU"
        self.modo = "HI"              
        self.metodo = "alfabeta"
        self.t_global = 0.0
        self.salir = False
        self.ayuda = False            
        self.mensaje = ""
        self.sub = ""
        self.registro = {"minimax": [], "alfabeta": []}
        self.comp = {"estado": "pendiente", "datos": None}

    def iniciar_comparacion(self):
        """Calcula en segundo plano Minimax vs Alfa-Beta desde el estado inicial."""
        if self.comp["estado"] != "pendiente":
            return
        self.comp["estado"] = "calculando"

        def trabajo():
            try:
                self.comp["datos"] = comparar_desde_inicio()
                self.comp["estado"] = "listo"
            except Exception:
                self.comp["estado"] = "error"

        threading.Thread(target=trabajo, daemon=True).start()

    def humano(self, j):
        return (j == "A" and self.modo == "HI") or (j == "B" and self.modo == "IH")

    def etiqueta_jugador(self, j):
        if self.humano(j):
            return "Humano"
        return "IA · " + NOMBRE_METODO[self.metodo]

    def nueva_partida(self):
        self.max_tiros = reglas.maxTiros
        self.turno = "A"
        self.restantes = self.max_tiros
        self.mano = {"A": None, "B": None}
        self.dados = {"A": None, "B": None}
        self.tiros = {"A": 0, "B": 0}
        self.dados_mesa = None
        self.angulos = (0.0, 0.0)
        self.destino = (1, 1)
        self.anim_t = 0.0
        self.caras_tmp = (1, 1)
        self.registro = {"minimax": [], "alfabeta": []}
        self.ia_accion = None
        self.resultado = None
        self.timer = 0.0
        self.continuar = None
        self.entrar_espera_lanzar()

    def volver_menu(self):
        self.fase = "MENU"
        self.ayuda = False

    def entrar_espera_lanzar(self):
        t = self.turno
        self.fase = "ESPERA_LANZAR"
        if self.humano(t):
            self.mensaje = f"Turno del jugador {t}: lanza los dados"
            self.sub = "Pulsa LANZAR DADOS (o la tecla ESPACIO)"
        else:
            self.timer = 0.9
            self.mensaje = f"Jugador {t} (IA) se prepara para lanzar"
            self.sub = f"Lanzamientos disponibles: {self.restantes}"

    def iniciar_lanzamiento(self):
        t = self.turno
        self.destino = random.choice(RESULTADOS)
        self.angulos = (random.uniform(-14, 14), random.uniform(-14, 14))
        self.caras_tmp = (random.randint(1, 6), random.randint(1, 6))
        self.anim_t = 0.0
        self.dados_mesa = None
        self.fase = "LANZANDO"
        n = self.tiros[t] + 1
        self.mensaje = f"Jugador {t} lanza los dados"
        self.sub = f"Lanzamiento {n} de {self.max_tiros}"

    def terminar_lanzamiento(self):
        t = self.turno
        d1, d2 = self.destino
        v = valor(d1, d2)
        self.dados[t] = (d1, d2)
        self.mano[t] = v
        self.tiros[t] += 1
        self.restantes -= 1
        self.dados_mesa = (d1, d2)
        self.fase = "MOSTRAR"
        self.timer = 0.9
        self.mensaje = f"Jugador {t} sacó {d1} y {d2}  →  {nombre(v)}"
        self.sub = f"Lanzamiento {self.tiros[t]} de {self.max_tiros}"

    def despues_de_mostrar(self):
        t = self.turno
        if self.mano[t] == 1000:
            self.plantarse("¡Es el 21, la jugada máxima!")
        elif self.restantes == 0:
            self.plantarse("No le quedan lanzamientos.")
        elif self.humano(t):
            self.fase = "ESPERA_DECISION"
            self.mensaje = f"Jugador {t}: ¿te plantas o relanzas?"
            self.sub = f"Te quedan {self.restantes} lanzamiento(s)  ·  P = plantarse, R = relanzar"
        else:
            self.pensar_ia()

    def pensar_ia(self):
        """La IA evalúa sus opciones con Minimax o Alfa-Beta (tarda milisegundos)."""
        t = self.turno
        if t == "A":
            estado = ("DECIDE_A", self.mano["A"], None, self.restantes)
        else:
            estado = ("DECIDE_B", self.mano["A"], self.mano["B"], self.restantes)
        # Se evalúa el mismo estado con los DOS algoritmos para poder compararlos.
        # La acción que se juega es la del algoritmo elegido en el menú.
        otro = "minimax" if self.metodo == "alfabeta" else "alfabeta"
        for metodo in (self.metodo, otro):
            accion, val, nodos, podas, seg = mejor_accion(estado, metodo)
            self.registro[metodo].append(
                {"jugador": t, "lanz": self.tiros[t], "accion": accion,
                 "valor": round(val, 10) + 0.0, "nodos": nodos,
                 "podas": podas, "seg": seg})
            if metodo == self.metodo:
                self.ia_accion = accion
        self.fase = "PENSANDO"
        self.timer = 0.7
        self.mensaje = f"La IA (jugador {t}) está pensando"
        self.sub = f"Evaluando con {NOMBRE_METODO[self.metodo]}"

    def anunciar_ia(self):
        t = self.turno
        self.fase = "ANUNCIO_IA"
        self.timer = 1.3
        self.mensaje = f"La IA (jugador {t}) decide: {self.ia_accion.upper()}"
        self.sub = "Mira el recuadro inferior para ver nodos, podas y tiempo"

    def plantarse(self, motivo=""):
        t = self.turno
        self.mensaje = f"Jugador {t} se planta con {nombre(self.mano[t])}"
        self.sub = motivo
        self.fase = "PAUSA"
        self.timer = 1.5
        if t == "A":
            self.continuar = self.pasar_a_b
        else:
            self.continuar = self.terminar_partida

    def pasar_a_b(self):
        self.turno = "B"
        self.restantes = self.max_tiros
        self.dados_mesa = None
        self.entrar_espera_lanzar()
        self.sub = "B conoce la jugada final de A. " + self.sub

    def terminar_partida(self):
        self.resultado = utilidad(self.mano["A"], self.mano["B"])
        self.fase = "FIN"

    def botones(self):
        f = self.fase
        bs = []
        if f == "MENU":
            if self.ayuda:
                return [Boton("cerrar_ayuda", pygame.Rect(
                    CX - 120, AYUDA_TARJETA.bottom - 66, 240, 50), "ENTENDIDO", tam=24)]
            modos = [("HI", "HUMANO (A) VS IA (B)"), ("IH", "IA (A) VS HUMANO (B)"),
                     ("II", "IA VS IA")]
            for i, (k, e) in enumerate(modos):
                bs.append(Boton("modo:" + k, pygame.Rect(CX - 210, 254 + i * 38, 420, 36),
                                e, seleccionado=(self.modo == k), tam=26, estilo="texto"))
            algos = [("minimax", "MINIMAX"), ("alfabeta", "PODA ALFA-BETA")]
            for i, (k, e) in enumerate(algos):
                bs.append(Boton("algo:" + k, pygame.Rect(CX - 210, 402 + i * 38, 420, 36),
                                e, seleccionado=(self.metodo == k), tam=26, estilo="texto"))
            bs.append(Boton("jugar", pygame.Rect(CX - 210, 488, 420, 56), "JUGAR",
                            tam=44, estilo="texto"))
            bs.append(Boton("ayuda", pygame.Rect(CX - 210, 554, 420, 36), "CÓMO SE JUEGA",
                            tam=26, estilo="texto"))
            bs.append(Boton("salir", pygame.Rect(CX - 210, 592, 420, 36), "SALIR",
                            tam=26, estilo="texto"))
            return bs
        if f == "FIN":
            y = FIN_TARJETA.bottom - 64
            bs.append(Boton("nueva", pygame.Rect(318, y, 220, 50), "NUEVA PARTIDA", tam=22))
            bs.append(Boton("menu", pygame.Rect(562, y, 220, 50), "MENÚ", color=AZUL, tam=22))
            return bs
        bs.append(Boton("menu", pygame.Rect(986, 22, 86, 38), "MENÚ", color=GRIS, tam=18))
        if f == "ESPERA_LANZAR" and self.humano(self.turno):
            bs.append(Boton("lanzar", pygame.Rect(780, 598, 280, 62), "LANZAR DADOS", tam=26))
        if f == "ESPERA_DECISION":
            bs.append(Boton("plantarse", pygame.Rect(690, 598, 180, 62), "PLANTARSE",
                            color=VERDE, tam=22))
            bs.append(Boton("relanzar", pygame.Rect(886, 598, 174, 62), "RELANZAR", tam=22))
        return bs

    def accion(self, clave):
        if clave == "jugar" or clave == "nueva":
            self.nueva_partida()
        elif clave.startswith("modo:"):
            self.modo = clave[5:]
        elif clave.startswith("algo:"):
            self.metodo = clave[5:]
        elif clave == "lanzar" or clave == "relanzar":
            self.iniciar_lanzamiento()
        elif clave == "plantarse":
            self.plantarse("Decisión del jugador.")
        elif clave == "menu":
            self.volver_menu()
        elif clave == "ayuda":
            self.ayuda = True
        elif clave == "cerrar_ayuda":
            self.ayuda = False
        elif clave == "salir":
            self.salir = True

    def manejar(self, ev):
        disponibles = {b.clave: b for b in self.botones()}
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for b in disponibles.values():
                if b.rect.collidepoint(ev.pos):
                    self.accion(b.clave)
                    return
        elif ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                for clave in ("cerrar_ayuda", "jugar", "lanzar", "nueva"):
                    if clave in disponibles:
                        self.accion(clave)
                        return
            elif ev.key == pygame.K_p and "plantarse" in disponibles:
                self.accion("plantarse")
            elif ev.key == pygame.K_r and "relanzar" in disponibles:
                self.accion("relanzar")
            elif ev.key == pygame.K_ESCAPE:
                if self.ayuda:
                    self.ayuda = False
                elif self.fase == "MENU":
                    self.salir = True
                else:
                    self.volver_menu()

    def actualizar(self, dt):
        self.t_global += dt
        f = self.fase
        if f == "ESPERA_LANZAR" and not self.humano(self.turno):
            self.timer -= dt
            if self.timer <= 0:
                self.iniciar_lanzamiento()
        elif f == "LANZANDO":
            self.anim_t += dt
            t = self.anim_t
            if t < T_SALEN_DADOS + 0.9 and int(t / 0.07) != int((t - dt) / 0.07):
                self.caras_tmp = (random.randint(1, 6), random.randint(1, 6))
            if self.anim_t >= DURACION_LANZ:
                self.terminar_lanzamiento()
        elif f == "MOSTRAR":
            self.timer -= dt
            if self.timer <= 0:
                self.despues_de_mostrar()
        elif f == "PENSANDO":
            self.timer -= dt
            if self.timer <= 0:
                self.anunciar_ia()
        elif f == "ANUNCIO_IA":
            self.timer -= dt
            if self.timer <= 0:
                if self.ia_accion == "plantarse":
                    self.plantarse("Decisión de la IA.")
                else:
                    self.iniciar_lanzamiento()
        elif f == "PAUSA":
            self.timer -= dt
            if self.timer <= 0:
                self.continuar()


    def dibujar(self, p):
        p.fill(FONDO)
        if self.fase == "MENU":
            self.dibujar_menu(p)
            if self.ayuda:
                self.dibujar_ayuda(p)
        else:
            self.dibujar_cabecera(p)
            self.dibujar_mesa(p)
            self.dibujar_paneles(p)
            self.dibujar_barra(p)
            if self.fase == "FIN":
                self.dibujar_fin(p)
        pos = pygame.mouse.get_pos()
        for b in self.botones():
            b.dibujar(p, b.rect.collidepoint(pos))

    def dibujar_menu(self, p):
        p.blit(superficie_fondo_menu(), (0, 0))
        # título con líneas decorativas doradas
        for y, mitad in ((46, 190), (56, 120), (168, 120), (178, 190)):
            pygame.draw.line(p, ORO, (CX - mitad, y), (CX + mitad, y), 3)
        rombo(p, CX, 28, 9, ORO)
        rombo(p, CX, 196, 9, ORO)
        texto(p, "JUEGO 21", 78, (40, 26, 12), (CX + 3, 115), "center", True, True)
        texto(p, "JUEGO 21", 78, ORO, (CX, 112), "center", True, True)
        texto(p, "Búsqueda con contrincantes: Minimax y Poda Alfa-Beta", 17,
              (170, 150, 110), (CX, 216), "center")
        texto(p, "MODO DE JUEGO", 15, (170, 150, 110), (CX, 240), "center", True)
        texto(p, "ALGORITMO DE LA IA", 15, (170, 150, 110), (CX, 384), "center", True)

    def dibujar_ayuda(self, p):
        """Recuadro con la explicación del juego (se abre con CÓMO SE JUEGA)."""
        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((4, 6, 10, 215))
        p.blit(velo, (0, 0))
        t = AYUDA_TARJETA
        pygame.draw.rect(p, PANEL, t, border_radius=22)
        pygame.draw.rect(p, ORO, t, 4, border_radius=22)
        texto(p, "CÓMO SE JUEGA", 40, ORO, (CX, t.y + 44), "center", True, True)
        pygame.draw.line(p, ORO, (CX - 120, t.y + 76), (CX + 120, t.y + 76), 2)
        n = reglas.maxTiros
        puntos = [
            "Juegan dos jugadores: A (MAX) y B (MIN). Juega A primero y luego B, "
            "que ya conoce la jugada final de A.",
            f"En cada lanzamiento se tiran 2 dados con el cubilete. "
            f"Cada jugador tiene hasta {n} lanzamientos.",
            "Tras cada lanzamiento se decide: PLANTARSE (conservar la jugada) o "
            "RELANZAR (la nueva jugada reemplaza a la anterior).",
            "Ranking: 21 (el 2 y el 1) > dobles (66 ... 11) > 65 > 64 > ... > 31. "
            "Gana la jugada más alta; si empatan, hay empate.",
            "La IA decide con Minimax (Expectiminimax, con nodos de azar) o con Poda "
            "Alfa-Beta: elige la acción de mayor utilidad esperada.",
            "Utilidad: +1 si gana A, −1 si gana B, 0 si empatan. A busca el valor "
            "más alto y B el más bajo.",
        ]
        y = t.y + 98
        for i, txt in enumerate(puntos, start=1):
            lineas = partir_lineas(txt, 19, 700)
            pygame.draw.circle(p, ORO, (t.x + 50, y + 13), 15)
            texto(p, str(i), 18, (20, 24, 28), (t.x + 50, y + 13), "center", True)
            for k, linea in enumerate(lineas):
                texto(p, linea, 19, BLANCO, (t.x + 84, y + k * 26), "topleft")
            y += max(len(lineas) * 26, 30) + 14
        texto(p, "Controles:  ESPACIO lanzar   ·   P plantarse   ·   R relanzar   ·   ESC menú",
              17, ORO, (CX, t.bottom - 92), "center")

    def dibujar_cabecera(self, p):
        texto(p, "JUEGO 21", 40, ORO, (36, 14), "topleft", True)
        texto(p, "Minimax y Poda Alfa-Beta", 17, GRIS, (38, 62))
        # recuadro del turno
        if self.fase == "FIN":
            etiqueta, color = "PARTIDA TERMINADA", BLANCO
        else:
            etiqueta = f"TURNO DEL JUGADOR {self.turno}  ({'MAX' if self.turno == 'A' else 'MIN'})"
            color = COLOR_JUGADOR[self.turno]
        r = pygame.Rect(0, 0, 430, 54)
        r.center = (CX, 46)
        pygame.draw.rect(p, PANEL, r, border_radius=14)
        pygame.draw.rect(p, color, r, 3, border_radius=14)
        texto(p, etiqueta, 26, color, r.center, "center", True)
        chip = pygame.Rect(770, 24, 190, 34)
        pygame.draw.rect(p, PANEL, chip, border_radius=17)
        texto(p, "IA: " + NOMBRE_METODO[self.metodo], 17, BLANCO, chip.center, "center", True)

    def dibujar_mesa(self, p):
        pygame.draw.rect(p, MADERA, (306, 108, 488, 380), border_radius=40)
        pygame.draw.rect(p, PANO, (320, 122, 460, 352), border_radius=30)
        pygame.draw.rect(p, PANO_OSC, (320, 122, 460, 352), 3, border_radius=30)
        pygame.draw.rect(p, PANO_OSC, (340, 142, 420, 312), 2, border_radius=22)

        lanzando = self.fase == "LANZANDO"
        t = self.anim_t
        # dados sobre la mesa
        if lanzando:
            if t >= T_SALEN_DADOS:
                u = min(1.0, (t - T_SALEN_DADOS) / 1.05)
                for i in range(2):
                    x0, y0 = CX + 66, 236
                    x1, y1 = POS_DADOS[i]
                    x = x0 + (x1 - x0) * suave(u) + (i * 2 - 1) * 8 * (1 - u)
                    rebote = 95 * (1 - u) * abs(math.sin(u * math.pi * 3))
                    y = y0 + (y1 - y0) * u - rebote
                    giro = (1 - u) * 560 * (1 if i == 0 else -1) + self.angulos[i]
                    cara = self.destino[i] if u > 0.84 else self.caras_tmp[i]
                    dibujar_sombra(p, x, y1 + 46, DADO_TAM, int(90 - rebote * 0.6))
                    dibujar_dado(p, x, y, DADO_TAM, cara, giro)
        elif self.dados_mesa:
            for i in range(2):
                x, y = POS_DADOS[i]
                dibujar_sombra(p, x, y + 46, DADO_TAM, 90)
                dibujar_dado(p, x, y, DADO_TAM, self.dados_mesa[i], self.angulos[i])
        else:
            texto(p, "Aquí aparecerán los dados", 18, (120, 190, 160),
                  (CX, 392), "center")

        # cubilete
        if lanzando:
            x, y, ang = pose_cubilete(t)
        else:
            x, y, ang = CX, 214, 0
        cub = superficie_cubilete()
        if ang:
            cub = pygame.transform.rotozoom(cub, ang, 1.0)
        dibujar_sombra(p, CX, 318, 120, 70)
        p.blit(cub, cub.get_rect(center=(int(x), int(y))))

    def dibujar_paneles(self, p):
        for j, x in (("A", 36), ("B", 814)):
            activo = (self.fase not in ("FIN", "MENU")) and self.turno == j
            color = COLOR_JUGADOR[j]
            r = pygame.Rect(x, 108, 250, 380)
            pygame.draw.rect(p, PANEL, r, border_radius=18)
            if activo:
                brillo = pygame.Surface((r.width + 24, r.height + 24), pygame.SRCALPHA)
                pygame.draw.rect(brillo, color + (60,), (0, 0, r.width + 24, r.height + 24),
                                 border_radius=28)
                p.blit(brillo, (r.x - 12, r.y - 12))
                pygame.draw.rect(p, PANEL, r, border_radius=18)
                pygame.draw.rect(p, color, r, 4, border_radius=18)
            else:
                pygame.draw.rect(p, (52, 68, 78), r, 2, border_radius=18)
            cx = r.centerx
            texto(p, f"JUGADOR {j}", 30, color, (cx, r.y + 34), "center", True)
            rol = "MAX" if j == "A" else "MIN"
            texto(p, f"{rol}  ·  {self.etiqueta_jugador(j)}", 17, GRIS,
                  (cx, r.y + 68), "center")
            if activo:
                texto(p, "● JUGANDO", 18, color, (cx, r.y + 98), "center", True)
            elif self.fase != "FIN" and j == "B" and self.turno == "A":
                texto(p, "esperando su turno", 16, GRIS, (cx, r.y + 98), "center")
            # jugada actual
            m = self.mano[j]
            if self.fase == "LANZANDO" and self.turno == j:
                grande = "..."
            elif m is None:
                grande = "—"
            else:
                grande = nombre(m)
            texto(p, grande, 62 if len(grande) <= 3 else 44, BLANCO,
                  (cx, r.y + 170), "center", True)
            texto(p, "JUGADA", 14, GRIS, (cx, r.y + 214), "center", True)
            # dados pequeños de ese jugador
            d = self.dados[j]
            for i in range(2):
                px = cx - 38 + i * 76
                if d and not (self.fase == "LANZANDO" and self.turno == j):
                    dibujar_dado(p, px, r.y + 280, 56, d[i])
                else:
                    pygame.draw.rect(p, (34, 50, 60), (px - 28, r.y + 252, 56, 56),
                                     border_radius=11)
            usados = self.tiros[j]
            texto(p, f"Lanzamientos: {usados} de {self.max_tiros}", 17, GRIS,
                  (cx, r.y + 342), "center")

    def dibujar_barra(self, p):
        msg = self.mensaje
        if self.fase in ("PENSANDO", "LANZANDO"):
            msg += "." * (int(self.t_global * 3) % 4)
        texto(p, msg, 27, BLANCO, (40, 506), "topleft", True)
        texto(p, self.sub, 18, GRIS, (42, 544))
        self.dibujar_registro(p)

    def dibujar_registro(self, p):
        """Recuadro inferior izquierdo: registro de la IA en tiempo real."""
        caja = pygame.Rect(40, 576, 620, 118)
        pygame.draw.rect(p, PANEL, caja, border_radius=12)
        texto(p, f"REGISTRO DE LA IA EN TIEMPO REAL  ·  {NOMBRE_METODO[self.metodo]}",
              14, GRIS, (caja.x + 16, caja.y + 8), "topleft", True)
        reg = self.registro[self.metodo]
        if not reg:
            texto(p, "Aún no ha decidido la IA. Aquí se irán sumando sus resultados.",
                  17, GRIS, (caja.x + 16, caja.y + 50))
            return
        col = {"u": caja.x + 356, "n": caja.x + 450, "p": caja.x + 528, "t": caja.x + 604}
        y = caja.y + 30
        for clave, etiqueta in (("u", "Utilidad"), ("n", "Nodos"),
                                ("p", "Podas"), ("t", "Tiempo")):
            texto(p, etiqueta, 13, GRIS, (col[clave], y), "topright", True)
        y += 19
        for r in reg[-2:]:                       # las 2 decisiones más recientes
            texto(p, f"{r['jugador']} · lanz. {r['lanz']} → {r['accion'].upper()}",
                  16, COLOR_JUGADOR[r["jugador"]], (caja.x + 16, y), "topleft", True)
            texto(p, f"{r['valor']:+.3f}", 16, BLANCO, (col["u"], y), "topright")
            texto(p, f"{r['nodos']:,}", 16, BLANCO, (col["n"], y), "topright")
            texto(p, f"{r['podas']:,}", 16, BLANCO, (col["p"], y), "topright")
            texto(p, fmt_tiempo(r["seg"]), 16, BLANCO, (col["t"], y), "topright")
            y += 20
        # fila acumulada: suma de TODAS las decisiones de la partida
        y += 3
        pygame.draw.line(p, (52, 68, 78), (caja.x + 16, y), (caja.right - 16, y), 1)
        y += 4
        n = len(reg)
        texto(p, f"ACUMULADO ({n} " + ("decisión" if n == 1 else "decisiones") + ")", 16, ORO,
              (caja.x + 16, y), "topleft", True)
        texto(p, "—", 16, ORO, (col["u"], y), "topright", True)
        texto(p, f"{sum(r['nodos'] for r in reg):,}", 16, ORO, (col["n"], y), "topright", True)
        texto(p, f"{sum(r['podas'] for r in reg):,}", 16, ORO, (col["p"], y), "topright", True)
        texto(p, fmt_tiempo(sum(r["seg"] for r in reg)), 16, ORO,
              (col["t"], y), "topright", True)

    def dibujar_tabla(self, p, x, y, titulo, filas):
        """Tabla Minimax vs Alfa-Beta de 420 px de ancho."""
        texto(p, titulo, 15, GRIS, (x, y), "topleft", True)
        y += 30
        texto(p, "Métrica", 14, GRIS, (x, y), "topleft", True)
        texto(p, "Minimax", 15, COLOR_MINIMAX, (x + 300, y), "topright", True)
        texto(p, "Alfa-Beta", 15, COLOR_ALFABETA, (x + 420, y), "topright", True)
        y += 26
        pygame.draw.line(p, (52, 68, 78), (x, y), (x + 420, y), 1)
        y += 8
        for etiqueta, a, b, mejor in filas:
            texto(p, etiqueta, 17, GRIS, (x, y + 1), "topleft")
            tam = 18 if max(len(a), len(b)) <= 10 else 14   # textos largos, más chicos
            texto(p, a, tam, VERDE if mejor in ("mm", "ambos") else BLANCO,
                  (x + 296, y + (18 - tam) // 2), "topright", True)
            texto(p, b, tam, VERDE if mejor in ("ab", "ambos") else BLANCO,
                  (x + 420, y + (18 - tam) // 2), "topright", True)
            y += 34

    def dibujar_fin(self, p):
        velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        velo.fill((6, 10, 14, 205))
        p.blit(velo, (0, 0))
        tarjeta = FIN_TARJETA
        pygame.draw.rect(p, PANEL, tarjeta, border_radius=22)
        u = self.resultado
        if u > 0:
            titulo, color = "GANA EL JUGADOR A", COLOR_JUGADOR["A"]
        elif u < 0:
            titulo, color = "GANA EL JUGADOR B", COLOR_JUGADOR["B"]
        else:
            titulo, color = "EMPATE", BLANCO
        pygame.draw.rect(p, color, tarjeta, 4, border_radius=22)
        y0 = tarjeta.y
        texto(p, "FIN DE LA PARTIDA", 16, GRIS, (CX, y0 + 26), "center", True)
        texto(p, titulo, 40, color, (CX, y0 + 62), "center", True)
        texto(p, f"Jugador A: {nombre(self.mano['A'])}   ·   "
                 f"Jugador B: {nombre(self.mano['B'])}   ·   Utilidad del juego: {u:+d}",
              19, BLANCO, (CX, y0 + 106), "center")
        humanos = [j for j in "AB" if self.humano(j)]
        if len(humanos) == 1 and u != 0:
            gano = (u > 0) == (humanos[0] == "A")
            texto(p, "¡Ganaste!" if gano else "Ganó la IA", 21, VERDE if gano else ROJO,
                  (CX, y0 + 136), "center", True)

        # ---- comparación Minimax vs Alfa-Beta ----
        x_izq, x_der, y_tab = 90, 590, y0 + 170
        pygame.draw.line(p, (52, 68, 78), (CX, y_tab), (CX, y_tab + 258), 1)

        rm, ra = self.registro["minimax"], self.registro["alfabeta"]
        igual_partida = None
        evit_partida = None
        if rm:
            um = "/".join(f"{r['valor']:+.3f}" for r in rm[-2:])
            ua = "/".join(f"{r['valor']:+.3f}" for r in ra[-2:])
            igual_partida = all(abs(a["valor"] - b["valor"]) < 1e-9 and
                                a["accion"] == b["accion"] for a, b in zip(rm, ra))
            nm, na = sum(r["nodos"] for r in rm), sum(r["nodos"] for r in ra)
            filas = armar_filas(um, ua, igual_partida, nm, na,
                                sum(r["podas"] for r in rm), sum(r["podas"] for r in ra),
                                sum(r["seg"] for r in rm), sum(r["seg"] for r in ra))
            evit_partida = 100 * (1 - na / nm) if nm else 0.0
            self.dibujar_tabla(p, x_izq, y_tab,
                               f"EN ESTA PARTIDA  ·  {len(rm)} decisión(es) de la IA", filas)
        else:
            texto(p, "EN ESTA PARTIDA", 15, GRIS, (x_izq, y_tab), "topleft", True)
            texto(p, "La IA no tuvo que decidir en esta partida.", 18, GRIS,
                  (x_izq, y_tab + 60))

        igual_total = None
        evit_total = None
        titulo_der = "DESDE EL INICIO DEL JUEGO  ·  árbol completo"
        if self.comp["estado"] == "listo":
            d = self.comp["datos"]
            vm, nm2, pm, tm = d["minimax"]
            va, na2, pa, ta = d["alfabeta"]
            igual_total = abs(vm - va) < 1e-9
            evit_total = 100 * (1 - na2 / nm2)
            filas = armar_filas(f"{vm:+.4f}", f"{va:+.4f}", igual_total,
                                nm2, na2, pm, pa, tm, ta)
            self.dibujar_tabla(p, x_der, y_tab, titulo_der, filas)
        else:
            texto(p, titulo_der, 15, GRIS, (x_der, y_tab), "topleft", True)
            msg = ("Calculando la comparación completa..."
                   if self.comp["estado"] in ("pendiente", "calculando")
                   else "No se pudo calcular la comparación completa.")
            texto(p, msg, 18, GRIS, (x_der, y_tab + 60))

        # ---- conclusiones ----
        y = y_tab + 276
        if igual_partida is not None or igual_total is not None:
            todo_igual = (igual_partida in (True, None)) and (igual_total in (True, None))
            if todo_igual:
                texto(p, "Los dos algoritmos eligieron las mismas acciones con la misma utilidad.",
                      18, VERDE, (CX, y), "center", True)
            else:
                texto(p, "Atención: los algoritmos no coincidieron, revisa el código.",
                      18, ROJO, (CX, y), "center", True)
        partes = []
        if evit_partida is not None:
            partes.append(f"{evit_partida:.1f} % de los nodos en esta partida")
        if evit_total is not None:
            partes.append(f"{evit_total:.1f} % desde el inicio del juego")
        if partes:
            texto(p, "Alfa-Beta evitó " + " y ".join(partes) + ".", 18, BLANCO,
                  (CX, y + 30), "center")


# ---------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Juego 21 - Minimax y Alfa-Beta")
    reloj = pygame.time.Clock()
    juego = Juego()
    juego.iniciar_comparacion()       # se calcula mientras estás en el menú
    while not juego.salir:
        dt = min(reloj.tick(FPS) / 1000.0, 0.05)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                juego.salir = True
            else:
                juego.manejar(ev)
        juego.actualizar(dt)
        juego.dibujar(pantalla)
        pygame.display.flip()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
