"""Mesa animada para el Juego del 21 con dos agentes adversarios."""

from __future__ import annotations

import math
import random
import tkinter as tk
from tkinter import messagebox, ttk

from alfa_beta import BuscadorAlfaBeta
from configuracion import (
    DURACION_LANZAMIENTO_MS,
    JUGADOR_HUMANO,
    MAX_TIROS,
    PAUSA_ENTRE_JUGADAS_MS,
)
from minimax import BuscadorMinimax
from motor import (
    ACCION_PLANTARSE,
    ACCION_TIRAR,
    Estado,
    acciones_disponibles,
    ganador,
    lanzar_dados,
    plantarse,
    registrar_resultado,
    resultado_de_dados,
)

FONDO = "#10171D"
PANEL = "#1B262D"
CLARO = "#F5F1E7"
APAGADO = "#9BABAF"
ORO = "#EBC77B"
VERDE = "#A1E9BF"
MADERA = "#744329"
ROJO = "#ED8A7D"
ANCHO = 1180
ALTO = 640

PUNTOS = {
    1: ((0, 0),),
    2: ((-1, -1), (1, 1)),
    3: ((-1, -1), (0, 0), (1, 1)),
    4: ((-1, -1), (1, -1), (-1, 1), (1, 1)),
    5: ((-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)),
    6: ((-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)),
}


def centrar_ventana(ventana: tk.Misc, ancho: int, alto: int) -> None:
    """Calcula la posicion para abrir la ventana en el centro de la pantalla."""
    ventana.update_idletasks()
    ancho = min(ancho, ventana.winfo_screenwidth())
    alto = min(alto, ventana.winfo_screenheight())
    x = (ventana.winfo_screenwidth() - ancho) // 2
    y = (ventana.winfo_screenheight() - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")


class InterfazJuego:
    """Coordina percepciones, busqueda, animacion y transiciones del motor."""

    def __init__(self, ventana: tk.Tk, algoritmo: str, permitir_elegir: bool = False):
        """Prepara los datos y recursos que necesita este objeto."""
        self.ventana = ventana
        self.algoritmo = algoritmo
        self.permitir_elegir = permitir_elegir
        self.estado = Estado()
        self.max_tiros = MAX_TIROS
        self.activo = False
        self.animando = False
        self.terminado = False
        self.ronda = 1
        self.empates = 0
        self.ultima_tirada: tuple[int, int] | None = None
        self.jugador_ultima_tirada = 0
        self.jugador_lanzando = 0
        self.resultado_pendiente: tuple[int, int] | None = None
        self.fotograma = 0
        self.total_fotogramas = max(16, DURACION_LANZAMIENTO_MS // 75)
        self.mensaje = "Preparados para jugar"
        self.historial: list[str] = []
        self.total_nodos = 0
        self.total_azar = 0
        self.total_podas = 0
        self.total_tiempo = 0.0
        self.total_decisiones = 0
        self.evento_turno: str | None = None
        self.evento_animacion: str | None = None
        self.evento_resultados: str | None = None
        self.ventana_resultados: tk.Toplevel | None = None
        self.escala = 1.0
        self.origen_x = 0.0
        self.origen_y = 0.0
        self.aleatorio = random.Random()

        self.ventana.title("Juego del 21 | Mesa animada")
        centrar_ventana(self.ventana, 1190, 830)
        self.ventana.minsize(950, 720)
        self.ventana.configure(bg=FONDO)
        self.variable_tiros = tk.StringVar(value=str(MAX_TIROS))
        self.variable_algoritmo = tk.StringVar(value=algoritmo)
        self.variable_mensaje = tk.StringVar(value="Comienza la partida para lanzar el cubilete")

        self.crear_componentes()
        self.actualizar_controles()
        self.ventana.bind("<Configure>", self.redibujar_al_redimensionar)
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.ventana.after(100, self.dibujar_mesa)

    def crear_componentes(self) -> None:
        """Construye los selectores, la mesa y los botones de la partida."""
        cabecera = tk.Frame(self.ventana, bg=FONDO, height=92)
        cabecera.pack(fill="x", padx=28, pady=(17, 8))
        cabecera.pack_propagate(False)

        marca = tk.Frame(cabecera, bg=FONDO)
        marca.pack(side="left")
        tk.Label(marca, text="21", fg=ORO, bg=FONDO,
                 font=("Arial", 43, "bold")).pack(side="left", padx=(0, 14))
        nombres = tk.Frame(marca, bg=FONDO)
        nombres.pack(side="left", pady=10)
        tk.Label(nombres, text="EL JUEGO DEL 21", fg=CLARO, bg=FONDO,
                 font=("Arial", 19, "bold")).pack(anchor="w")
        tk.Label(nombres, text="LA MESA DE LOS DADOS",
                 fg=APAGADO, bg=FONDO, font=("Arial", 10)).pack(anchor="w", pady=(4, 0))

        opciones = tk.Frame(cabecera, bg=FONDO)
        opciones.pack(side="right", pady=8)
        tk.Label(opciones, text="ALGORITMO", bg=FONDO, fg=APAGADO,
                 font=("Arial", 9, "bold")).grid(row=0, column=0, padx=(0, 8))
        self.selector_algoritmo = ttk.Combobox(
            opciones, textvariable=self.variable_algoritmo,
            values=("Minimax", "Alfa-Beta"), state="readonly", width=12,
            font=("Arial", 11),
        )
        self.selector_algoritmo.grid(row=1, column=0, padx=(0, 14), pady=3)
        if not self.permitir_elegir:
            self.selector_algoritmo.configure(state="disabled")

        tk.Label(opciones, text="TIROS MAX.", bg=FONDO, fg=APAGADO,
                 font=("Arial", 9, "bold")).grid(row=0, column=1, padx=(0, 8))
        self.selector_tiros = tk.Spinbox(
            opciones, from_=1, to=6, width=4, textvariable=self.variable_tiros,
            justify="center", bg=PANEL, fg=CLARO, insertbackground=CLARO,
            buttonbackground=PANEL, relief="flat", font=("Arial", 12),
        )
        self.selector_tiros.grid(row=1, column=1, padx=(0, 16), pady=3)
        self.boton_inicio = self.crear_boton(opciones, "INICIAR", self.alternar,
                                             ORO, FONDO)
        self.boton_inicio.grid(row=1, column=2, padx=(0, 9))
        self.boton_reiniciar = self.crear_boton(opciones, "REINICIAR", self.reiniciar,
                                                PANEL, CLARO)
        self.boton_reiniciar.grid(row=1, column=3)

        exterior = tk.Frame(self.ventana, bg="#25382F", bd=0)
        exterior.pack(fill="both", expand=True, padx=22, pady=(2, 9))
        self.lienzo = tk.Canvas(exterior, bg="#1C312A", highlightthickness=0,
                                bd=0, relief="flat")
        self.lienzo.pack(fill="both", expand=True, padx=4, pady=4)
        self.lienzo.bind("<Configure>", self.redibujar_al_redimensionar)

        pie = tk.Frame(self.ventana, bg=FONDO, height=84)
        pie.pack(fill="x", padx=28, pady=(3, 17))
        pie.pack_propagate(False)
        texto = tk.Frame(pie, bg=FONDO)
        texto.pack(side="left", fill="both", expand=True, pady=10)
        tk.Label(texto, textvariable=self.variable_mensaje, bg=FONDO, fg=CLARO,
                 font=("Arial", 13, "bold"), anchor="w").pack(fill="x")
        tk.Label(texto, text="2 dados  ·  2 y 1 gana al instante  ·  Mayor suma si nadie lo consigue",
                 bg=FONDO, fg=APAGADO, font=("Arial", 10),
                 anchor="w").pack(fill="x", pady=5)

        botones = tk.Frame(pie, bg=FONDO)
        botones.pack(side="right", pady=13)
        self.boton_plantarse = self.crear_boton(
            botones, "PLANTARSE", lambda: self.accion_humana(ACCION_PLANTARSE),
            PANEL, CLARO)
        self.boton_plantarse.pack(side="left", padx=(0, 9))
        self.boton_tirar = self.crear_boton(
            botones, "LANZAR DADOS", lambda: self.accion_humana(ACCION_TIRAR),
            VERDE, FONDO)
        self.boton_tirar.pack(side="left")

    @staticmethod
    def crear_boton(padre: tk.Widget, texto: str, comando,
                    fondo: str, color: str) -> tk.Button:
        """Crea un boton con el estilo compartido y la accion indicada."""
        return tk.Button(padre, text=texto, command=comando, bg=fondo,
                         fg=color, activebackground=ORO, activeforeground=FONDO,
                         disabledforeground="#6A7679", relief="flat",
                         font=("Arial", 10, "bold"), padx=18, pady=10,
                         cursor="hand2", borderwidth=0)

    def redibujar_al_redimensionar(self, _evento=None) -> None:
        """Actualiza el dibujo cuando cambia el tamaño de la ventana."""
        if hasattr(self, "lienzo"):
            self.dibujar_mesa()

    def punto(self, x: float, y: float) -> tuple[float, float]:
        """Adapta una posicion de la mesa al tamaño actual del lienzo."""
        return self.origen_x + x * self.escala, self.origen_y + y * self.escala

    def caja(self, x1: float, y1: float, x2: float, y2: float) -> tuple:
        """Adapta las dos esquinas de una figura al lienzo."""
        return (*self.punto(x1, y1), *self.punto(x2, y2))

    def elipse(self, x1, y1, x2, y2, color, borde="", ancho=1) -> None:
        """Dibuja un ovalo con las medidas y colores indicados."""
        self.lienzo.create_oval(*self.caja(x1, y1, x2, y2), fill=color,
                                outline=borde, width=ancho * self.escala)

    def linea(self, puntos, color, ancho=2, suavizar=False) -> None:
        """Une los puntos indicados y ajusta el grosor a la escala."""
        coordenadas = [coordenada for x, y in puntos for coordenada in self.punto(x, y)]
        self.lienzo.create_line(*coordenadas, fill=color,
                                width=ancho * self.escala,
                                smooth=suavizar, capstyle="round")

    def poligono(self, puntos, color, borde="") -> None:
        """Dibuja una figura cerrada a partir de sus vertices."""
        coordenadas = [coordenada for x, y in puntos for coordenada in self.punto(x, y)]
        self.lienzo.create_polygon(*coordenadas, fill=color, outline=borde,
                                   smooth=False)

    def texto(self, x, y, texto, tamano, color, negrita=False,
              ancla="center") -> None:
        """Coloca un texto y adapta su tamaño a la escala de la mesa."""
        self.lienzo.create_text(*self.punto(x, y), text=texto, fill=color,
                                font=("Arial", max(7, int(tamano * self.escala)),
                                      "bold" if negrita else "normal"),
                                anchor=ancla)

    def rectangulo(self, x1, y1, x2, y2, color, borde="", ancho=1) -> None:
        """Dibuja un rectangulo adaptado al tamaño de la mesa."""
        self.lienzo.create_rectangle(*self.caja(x1, y1, x2, y2), fill=color,
                                     outline=borde, width=ancho * self.escala)

    def dibujar_tablero(self) -> None:
        """Dibuja la mesa y los datos de la ronda."""
        self.rectangulo(0, 0, ANCHO, ALTO, "#182820")
        for i in range(13):
            y = 28 + i * 48
            self.linea([(0, y), (ANCHO, y + 12)], "#1F352B", 1)
        self.elipse(20, 18, 1160, 618, "#221812", "#140F0B", 4)
        self.elipse(28, 21, 1152, 604, MADERA, "#BE8754", 3)
        for desplazamiento in range(3):
            self.elipse(40 + desplazamiento * 7, 33 + desplazamiento * 7,
                        1140 - desplazamiento * 7, 594 - desplazamiento * 7,
                        "#70432B" if desplazamiento < 2 else "#103D32",
                        "#3C251C" if desplazamiento < 2 else "#2B6C51", 2)
        self.elipse(72, 68, 1108, 558, "#0C513C", "#1D8760", 3)
        self.elipse(92, 88, 1088, 540, "#105D45", "#1A654B", 2)
        self.elipse(112, 110, 1068, 521, "#125842", "#1D6349", 1)
        for centro_x, centro_y in ((88, 293), (1092, 293), (590, 84), (590, 548)):
            self.elipse(centro_x - 3, centro_y - 3, centro_x + 3,
                        centro_y + 3, ORO)
        self.texto(590, 106, "LA SUERTE ESTA EN LOS DADOS", 12, "#A6CEAE", True)
        self.texto(590, 560, f"RONDA {self.ronda}    ·    {self.empates} EMPATES",
                   13, ORO, True)

    def dibujar_jugador(self, numero: int, x: int) -> None:
        """Muestra los puntos, tiros y situacion de un jugador."""
        activo = self.estado.turno == numero and not self.terminado
        if self.animando:
            activo = self.jugador_lanzando == numero
        suma = self.estado.suma_j1 if numero == 1 else self.estado.suma_j2
        tiros = self.estado.tiros_j1 if numero == 1 else self.estado.tiros_j2
        color_borde = ORO if activo else "#2D7960"
        self.elipse(x - 117, 171, x + 117, 440, "#0A3F31", color_borde, 3)
        self.texto(x, 212, f"JUGADOR {numero}", 15,
                   ORO if activo else "#DAE4D5", True)
        self.texto(x, 307, str(suma), 68, CLARO, True)
        self.texto(x, 350, "PUNTOS", 11, APAGADO, True)
        self.texto(x, 388, f"TIROS: {tiros} / {self.max_tiros}", 13,
                   VERDE if activo else "#C2D0C4", True)
        estado = "LANZANDO..." if self.animando and self.jugador_lanzando == numero else (
            "SU TURNO" if activo else ("PLANTADO" if (self.estado.terminado_j1 if numero == 1
                               else self.estado.terminado_j2) else "EN ESPERA"))
        if self.terminado:
            estado = "GANADOR" if ganador(self.estado) == numero else "FINALIZADO"
        self.texto(x, 463, estado, 12, ORO if activo else "#C3D4C8", True)

    def dibujar_cubilete(self, x: float, y: float, inclinacion: float = 0.0,
                         elevacion: float = 0.0) -> None:
        """Dibuja el cubilete con la inclinacion y altura de la animacion."""
        y -= elevacion
        i = inclinacion
        self.elipse(x - 70, y + 64, x + 70, y + 84, "#0B3A2B")
        self.poligono([(x - 59 + i, y - 49), (x + 57 + i, y - 49),
                       (x + 42 - i, y + 62), (x - 39 - i, y + 62)], "#3E2318")
        self.poligono([(x - 57 + i, y - 45), (x + 54 + i, y - 45),
                       (x + 39 - i, y + 57), (x - 37 - i, y + 57)], "#925334")
        self.poligono([(x - 45 + i, y - 35), (x - 26 + i, y - 35),
                       (x - 21 - i, y + 47), (x - 37 - i, y + 47)], "#AB6C46")
        self.poligono([(x + 34 + i, y - 35), (x + 47 + i, y - 35),
                       (x + 34 - i, y + 48), (x + 27 - i, y + 48)], "#6E3724")
        self.elipse(x - 59 + i, y - 60, x + 59 + i, y - 26, "#231610", ORO, 3)
        self.elipse(x - 48 + i, y - 54, x + 48 + i, y - 31, "#17110E")
        self.linea([(x - 34 - i, y + 48), (x + 35 - i, y + 48)], ORO, 4)
        self.texto(x, y + 9, "21", 28, ORO, True)

    def dibujar_dado(self, x: float, y: float, valor: int,
                     angulo: float = 0.0, tamano: float = 75) -> None:
        """Dibuja un dado girado con los puntos de su valor."""
        def giro(dx: float, dy: float) -> tuple[float, float]:
            """Gira una posicion alrededor del centro del dado."""
            r = math.radians(angulo)
            return x + dx * math.cos(r) - dy * math.sin(r), \
                y + dx * math.sin(r) + dy * math.cos(r)

        mitad = tamano / 2
        esquinas = [giro(-mitad, -mitad), giro(mitad, -mitad),
                    giro(mitad, mitad), giro(-mitad, mitad)]
        sombra = [(a + 8, b + 16) for a, b in esquinas]
        self.elipse(x - mitad + 5, y + mitad - 2,
                    x + mitad + 14, y + mitad + 23, "#073827")
        self.poligono(sombra, "#E4D8C2")
        self.poligono([esquinas[2], esquinas[3], sombra[3], sombra[2]], "#B8B09F")
        self.poligono([esquinas[1], esquinas[2], sombra[2], sombra[1]], "#C7BEAD")
        self.poligono(esquinas, "#FCF8E8", "#D1CABB")
        self.linea([giro(-mitad + 8, -mitad + 8),
                    giro(mitad - 8, -mitad + 8)], "#FFFFFF", 2)
        for columna, fila in PUNTOS[valor]:
            punto_x, punto_y = giro(columna * tamano * .25,
                                    fila * tamano * .25)
            radio = tamano * 0.065
            self.elipse(punto_x - radio, punto_y - radio,
                        punto_x + radio, punto_y + radio, "#1C2524")

    def dibujar_dados(self) -> None:
        """Muestra los dados en movimiento o la ultima tirada confirmada."""
        if self.animando:
            progreso = self.fotograma / self.total_fotogramas
            if progreso < 0.34:
                return
            proporcion = min(1.0, (progreso - .34) / .66)
            salto = abs(math.sin(proporcion * math.pi * 3)) * 32 * (1 - proporcion)
            desplazamiento = 160 * (1 - proporcion) ** 2
            valor_1, valor_2 = self.resultado_pendiente or (3, 4)
            if progreso < .89:
                valor_1 = self.aleatorio.randint(1, 6)
                valor_2 = self.aleatorio.randint(1, 6)
            self.dibujar_dado(504 + desplazamiento, 385 - salto,
                             valor_1, -13 + 460 * (1 - proporcion), 78)
            self.dibujar_dado(678 - desplazamiento, 397 - salto,
                             valor_2, 10 - 380 * (1 - proporcion), 78)
            return
        if self.ultima_tirada:
            self.dibujar_dado(504, 385, self.ultima_tirada[0], -13, 78)
            self.dibujar_dado(678, 397, self.ultima_tirada[1], 10, 78)
        else:
            self.texto(590, 390, "LOS DADOS APARECERAN AQUI", 12,
                       "#84B59A", True)

    def dibujar_mesa(self) -> None:
        """Ajusta la escala y vuelve a dibujar la mesa completa."""
        if not hasattr(self, "lienzo") or not self.lienzo.winfo_exists():
            return
        ancho = max(1, self.lienzo.winfo_width())
        alto = max(1, self.lienzo.winfo_height())
        self.escala = min(ancho / ANCHO, alto / ALTO)
        self.origen_x = (ancho - ANCHO * self.escala) / 2
        self.origen_y = (alto - ALTO * self.escala) / 2
        self.lienzo.delete("all")
        self.dibujar_tablero()
        self.dibujar_jugador(1, 213)
        self.dibujar_jugador(2, 967)
        if self.animando:
            progreso = self.fotograma / self.total_fotogramas
            temblor = math.sin(self.fotograma * 2.8) * 14 * (1 - progreso)
            levanta = 85 * max(0, min(1, (progreso - .24) * 6))
            self.dibujar_cubilete(590 + temblor, 250, temblor * .34, levanta)
        else:
            self.dibujar_cubilete(590, 238, 0, 36)
        self.dibujar_dados()
        if self.ultima_tirada and not self.animando:
            valores = self.ultima_tirada
            suma = resultado_de_dados(*valores)
            mensaje = "¡2 Y 1!" if suma == -1 else f"SUMA {suma}"
            self.texto(590, 500, mensaje, 19, ORO if suma == -1 else CLARO, True)
        if self.terminado:
            numero = ganador(self.estado)
            self.texto(590, 308, f"¡VICTORIA DEL JUGADOR {numero}!", 18, ORO, True)
        elif self.animando:
            self.texto(590, 164, "LANZANDO LOS DADOS...", 16, ORO, True)

    def actualizar_controles(self) -> None:
        """Habilita las acciones humanas validas y actualiza el mensaje y la mesa."""
        humano = (self.activo and not self.animando and not self.terminado and
                  self.estado.turno == JUGADOR_HUMANO)
        opciones = acciones_disponibles(self.estado, self.max_tiros)
        self.boton_tirar.configure(state="normal" if humano and
                                   ACCION_TIRAR in opciones else "disabled")
        self.boton_plantarse.configure(state="normal" if humano and
                                       ACCION_PLANTARSE in opciones else "disabled")
        self.variable_mensaje.set(self.mensaje)
        self.dibujar_mesa()

    def cancelar_eventos(self) -> None:
        """Cancela las tareas pendientes para evitar acciones despues de reiniciar o cerrar."""
        for nombre in ("evento_turno", "evento_animacion", "evento_resultados"):
            identificador = getattr(self, nombre)
            if identificador is not None:
                try:
                    self.ventana.after_cancel(identificador)
                except tk.TclError:
                    pass
                setattr(self, nombre, None)

    def reiniciar(self) -> None:
        """Limpia la partida anterior y deja los controles listos para empezar."""
        self.cancelar_eventos()
        if self.ventana_resultados and self.ventana_resultados.winfo_exists():
            self.ventana_resultados.destroy()
        self.ventana_resultados = None
        self.estado = Estado()
        self.activo = False
        self.animando = False
        self.terminado = False
        self.ronda = 1
        self.empates = 0
        self.ultima_tirada = None
        self.jugador_lanzando = 0
        self.resultado_pendiente = None
        self.mensaje = "Preparados para una nueva partida"
        self.historial.clear()
        self.total_nodos = 0
        self.total_azar = 0
        self.total_podas = 0
        self.total_tiempo = 0.0
        self.total_decisiones = 0
        self.selector_tiros.configure(state="normal")
        self.selector_algoritmo.configure(state="readonly" if self.permitir_elegir
                                           else "disabled")
        self.boton_inicio.configure(text="INICIAR")
        self.actualizar_controles()

    def alternar(self) -> None:
        """Inicia, pausa o continua la partida con las opciones seleccionadas."""
        if self.terminado:
            self.reiniciar()
        if self.activo:
            self.activo = False
            if self.evento_turno:
                self.ventana.after_cancel(self.evento_turno)
                self.evento_turno = None
            self.mensaje = "Partida pausada"
            self.boton_inicio.configure(text="CONTINUAR")
        else:
            try:
                numero = int(self.variable_tiros.get())
                if numero not in range(1, 7):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Numero incorrecto", "Selecciona de 1 a 6 tiros.")
                return
            self.max_tiros = numero
            self.algoritmo = self.variable_algoritmo.get()
            self.activo = True
            self.selector_tiros.configure(state="disabled")
            self.selector_algoritmo.configure(state="disabled")
            self.boton_inicio.configure(text="PAUSAR")
            self.mensaje = (f"Turno del jugador {self.estado.turno}"
                            if self.estado.turno else "Empate: comienza otra ronda")
            if not self.animando:
                self.programar_turno(350)
        self.actualizar_controles()

    def programar_turno(self, espera: int = PAUSA_ENTRE_JUGADAS_MS) -> None:
        """Programa la siguiente jugada y cancela cualquier turno pendiente anterior."""
        if self.evento_turno is not None:
            self.ventana.after_cancel(self.evento_turno)
        self.evento_turno = self.ventana.after(espera, self.paso_automatico)

    def paso_automatico(self) -> None:
        """Inicia otra ronda, espera al humano o pide una decision a la IA."""
        self.evento_turno = None
        if not self.activo or self.animando or self.terminado:
            return
        if self.estado.turno == 0 and not self.terminado:
            self.nueva_ronda()
            self.programar_turno(650)
            return
        if self.estado.turno == JUGADOR_HUMANO:
            self.mensaje = "Tu turno: lanza los dados o plantate"
            self.actualizar_controles()
            return
        if self.estado.turno == 0:
            return
        buscador = (BuscadorMinimax(self.max_tiros) if self.algoritmo == "Minimax"
                    else BuscadorAlfaBeta(self.max_tiros))
        decision = buscador.elegir_accion(self.estado)
        e = decision.estadisticas
        self.total_nodos += e.nodos
        self.total_azar += e.nodos_azar
        self.total_podas += e.podas
        self.total_tiempo += e.segundos
        self.total_decisiones += 1
        self.historial.append(f"J{self.estado.turno} decide {decision.accion} "
                              f"(U={decision.valor:+.4f})")
        self.ejecutar_accion(decision.accion)

    def accion_humana(self, accion: str) -> None:
        """Acepta la accion solo si corresponde al humano y esta permitida."""
        if (self.activo and not self.animando and not self.terminado
                and self.estado.turno == JUGADOR_HUMANO
                and accion in acciones_disponibles(self.estado, self.max_tiros)):
            self.historial.append(f"J{self.estado.turno} decide {accion} (humano)")
            self.ejecutar_accion(accion)

    def ejecutar_accion(self, accion: str) -> None:
        """Aplica plantarse o prepara la animacion de un lanzamiento."""
        jugador = self.estado.turno
        if accion == ACCION_PLANTARSE:
            self.estado = plantarse(self.estado)
            self.historial.append(f"J{jugador} se planta")
            self.mensaje = f"El jugador {jugador} se planta"
            self.procesar_fin_de_turno()
        elif accion == ACCION_TIRAR:
            self.jugador_lanzando = jugador
            self.resultado_pendiente = lanzar_dados()
            self.fotograma = 0
            self.animando = True
            self.mensaje = f"Jugador {jugador}: agitando el cubilete..."
            self.actualizar_controles()
            self.animar_lanzamiento()
        else:
            raise ValueError(f"Accion desconocida: {accion}")

    def animar_lanzamiento(self) -> None:
        """Avanza un fotograma y confirma los dados al terminar la animacion."""
        self.evento_animacion = None
        if not self.animando:
            return
        self.fotograma += 1
        self.dibujar_mesa()
        if self.fotograma < self.total_fotogramas:
            self.evento_animacion = self.ventana.after(75, self.animar_lanzamiento)
        else:
            self.finalizar_lanzamiento()

    def finalizar_lanzamiento(self) -> None:
        """Guarda los dados reales, actualiza el motor y procesa el cambio de turno."""
        dados = self.resultado_pendiente
        if dados is None:
            return
        self.animando = False
        self.ultima_tirada = dados
        self.jugador_ultima_tirada = self.jugador_lanzando
        valor = resultado_de_dados(*dados)
        self.estado = registrar_resultado(self.estado, valor, self.max_tiros)
        resultado = "¡2 Y 1!" if valor == -1 else str(valor)
        self.mensaje = f"Jugador {self.jugador_lanzando}: {dados[0]} y {dados[1]}  ·  {resultado}"
        self.historial.append(f"J{self.jugador_lanzando} lanza {dados[0]} y "
                              f"{dados[1]}: {resultado}")
        self.resultado_pendiente = None
        self.procesar_fin_de_turno()

    def procesar_fin_de_turno(self) -> None:
        """Continua la partida, repite un empate o anuncia al ganador."""
        if self.estado.turno == 0:
            resultado = ganador(self.estado)
            if resultado == 0:
                self.empates += 1
                self.mensaje = "Empate: comienza otra ronda"
                self.historial.append(f"Ronda {self.ronda} empatada")
                self.actualizar_controles()
                if self.activo:
                    self.programar_turno(1400)
                return
            self.terminado = True
            self.activo = False
            self.mensaje = f"¡El jugador {resultado} gana la partida!"
            self.historial.append(f"Partida terminada: gana J{resultado}")
            self.boton_inicio.configure(text="NUEVA PARTIDA")
            self.actualizar_controles()
            self.evento_resultados = self.ventana.after(1100, self.abrir_resultados)
            return
        self.actualizar_controles()
        if self.activo:
            self.programar_turno()

    def nueva_ronda(self) -> None:
        """Reinicia los puntos y tiros despues de un empate."""
        self.estado = Estado()
        self.ronda += 1
        self.ultima_tirada = None
        self.jugador_lanzando = 0
        self.historial.append(f"Comienza ronda {self.ronda}")
        self.mensaje = f"Ronda {self.ronda}: vuelve a comenzar el jugador 1"
        self.actualizar_controles()

    def abrir_resultados(self) -> None:
        """Muestra el ganador, el historial y la comparacion de los algoritmos."""
        self.evento_resultados = None
        if not self.terminado:
            return
        ganador_numero = ganador(self.estado)
        ventana = tk.Toplevel(self.ventana)
        self.ventana_resultados = ventana
        ventana.title("Resultado y evaluacion del algoritmo")
        centrar_ventana(ventana, 950, 700)
        ventana.minsize(840, 630)
        ventana.configure(bg=FONDO)
        ventana.transient(self.ventana)
        ventana.grab_set()

        tk.Label(ventana, text="FIN DE LA PARTIDA", bg=FONDO, fg=ORO,
                 font=("Arial", 14, "bold")).pack(pady=(18, 2))
        tk.Label(ventana, text=f"GANA EL JUGADOR {ganador_numero}",
                 bg=FONDO, fg=CLARO, font=("Arial", 28, "bold")).pack()
        motivo = ("Combinacion especial: 2 y 1" if self.estado.ganador_21 else
                  f"Mayor suma: {self.estado.suma_j1} contra {self.estado.suma_j2}")
        tk.Label(ventana, text=f"{motivo}  ·  {self.ronda} ronda(s)  ·  "
                 f"{self.empates} empate(s)", bg=FONDO, fg=APAGADO,
                 font=("Arial", 12)).pack(pady=(5, 19))

        cuerpo = tk.Frame(ventana, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=23)
        columna_partida = tk.Frame(cuerpo, bg=PANEL, padx=17, pady=14)
        columna_partida.pack(side="left", fill="both", expand=True, padx=(0, 8))
        columna_comparar = tk.Frame(cuerpo, bg=PANEL, padx=17, pady=14)
        columna_comparar.pack(side="left", fill="both", expand=True, padx=(8, 0))

        self.titulo_panel(columna_partida, "BUSQUEDAS DE ESTA PARTIDA")
        self.linea_panel(columna_partida, "Algoritmo", self.algoritmo)
        self.linea_panel(columna_partida, "Decisiones de IA", self.total_decisiones)
        self.linea_panel(columna_partida, "Estados evaluados", f"{self.total_nodos:,}")
        self.linea_panel(columna_partida, "Nodos de azar", f"{self.total_azar:,}")
        self.linea_panel(columna_partida, "Ramas evitadas", f"{self.total_podas:,}")
        self.linea_panel(columna_partida, "Tiempo total de IA",
                         f"{self.total_tiempo * 1000:.2f} ms")
        self.titulo_panel(columna_partida, "ULTIMOS MOVIMIENTOS")
        historial = tk.Text(columna_partida, height=11, width=35, bg="#121D22",
                            fg="#E4EAE5", relief="flat", wrap="word",
                            font=("Consolas", 10), borderwidth=8)
        historial.insert("1.0", "\n".join(self.historial[-12:]))
        historial.configure(state="disabled")
        historial.pack(fill="both", expand=True, pady=(5, 0))

        self.titulo_panel(columna_comparar, "COMPARACION DEL ESTADO INICIAL")
        primero = BuscadorMinimax(self.max_tiros).elegir_accion(Estado())
        segundo = BuscadorAlfaBeta(self.max_tiros).elegir_accion(Estado())
        for nombre, decision in (("MINIMAX", primero), ("ALFA-BETA", segundo)):
            tk.Label(columna_comparar, text=nombre, bg=PANEL, fg=ORO,
                     font=("Arial", 12, "bold")).pack(anchor="w", pady=(8, 4))
            e = decision.estadisticas
            self.linea_panel(columna_comparar, "Mejor accion", decision.accion)
            self.linea_panel(columna_comparar, "Utilidad esperada",
                             f"{decision.valor:+.6f}")
            self.linea_panel(columna_comparar, "Estados evaluados", f"{e.nodos:,}")
            self.linea_panel(columna_comparar, "Podas", e.podas)
            self.linea_panel(columna_comparar, "Tiempo", f"{e.segundos * 1000:.2f} ms")
        tk.Label(columna_comparar,
                 text="Comparacion desde el mismo estado y con el mismo maximo de tiros.\n"
                      "Una ronda empatada vale 0 en la busqueda; en la interfaz se repite.",
                 bg=PANEL, fg=APAGADO, font=("Arial", 9),
                 wraplength=385, justify="left").pack(anchor="w", pady=(16, 0))

        pie = tk.Frame(ventana, bg=FONDO)
        pie.pack(fill="x", padx=23, pady=15)
        self.crear_boton(pie, "NUEVA PARTIDA", lambda: self.reiniciar(),
                         VERDE, FONDO).pack(side="right")
        self.crear_boton(pie, "CERRAR ANALISIS", ventana.destroy,
                         PANEL, CLARO).pack(side="right", padx=9)

    @staticmethod
    def titulo_panel(padre: tk.Widget, texto: str) -> None:
        """Agrega un titulo a una seccion del analisis."""
        tk.Label(padre, text=texto, bg=PANEL, fg=VERDE,
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(7, 9))

    @staticmethod
    def linea_panel(padre: tk.Widget, etiqueta: str, valor) -> None:
        """Muestra una etiqueta y su valor en una fila del analisis."""
        fila = tk.Frame(padre, bg=PANEL)
        fila.pack(fill="x", pady=3)
        tk.Label(fila, text=etiqueta, bg=PANEL, fg=APAGADO,
                 font=("Arial", 10)).pack(side="left")
        tk.Label(fila, text=str(valor), bg=PANEL, fg=CLARO,
                 font=("Arial", 10, "bold")).pack(side="right")

    def cerrar(self) -> None:
        """Cancela las tareas pendientes y cierra la ventana."""
        self.cancelar_eventos()
        self.ventana.destroy()


def iniciar_interfaz(algoritmo: str, permitir_elegir: bool = False) -> None:
    """Crea la ventana con selector de algoritmo y mantiene la interfaz en marcha."""
    ventana = tk.Tk()
    ttk.Style(ventana).theme_use("clam")
    InterfazJuego(ventana, algoritmo, permitir_elegir)
    ventana.mainloop()
