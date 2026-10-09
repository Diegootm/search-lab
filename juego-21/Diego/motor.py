"""Reglas del Juego del 21, independientes del algoritmo de busqueda."""

from collections import Counter
from dataclasses import dataclass
from random import randint


ACCION_TIRAR = "Tirar"
ACCION_PLANTARSE = "Plantarse"
RESULTADO_21 = -1


@dataclass(frozen=True, slots=True)
class Estado:
    suma_j1: int = 0
    tiros_j1: int = 0
    suma_j2: int = 0
    tiros_j2: int = 0
    turno: int = 1
    ganador_21: int = 0


@dataclass(slots=True)
class Estadisticas:
    nodos: int = 0
    nodos_azar: int = 0
    hojas: int = 0
    podas: int = 0
    cache: int = 0
    segundos: float = 0.0


@dataclass(frozen=True, slots=True)
class Decision:
    accion: str
    valor: float
    estadisticas: Estadisticas


def crear_distribucion() -> tuple[tuple[int, float], ...]:
    conteos = Counter()
    for dado_1 in range(1, 7):
        for dado_2 in range(1, 7):
            valor = resultado_de_dados(dado_1, dado_2)
            conteos[valor] += 1
    return tuple(
        (valor, veces / 36)
        for valor, veces in sorted(conteos.items(), key=lambda par: par[0] != RESULTADO_21)
    )


def resultado_de_dados(dado_1: int, dado_2: int) -> int:
    if {dado_1, dado_2} == {1, 2}:
        return RESULTADO_21
    return dado_1 + dado_2


DISTRIBUCION = crear_distribucion()


def acciones_disponibles(estado: Estado, max_tiros: int) -> tuple[str, ...]:
    if estado.turno == 0:
        return ()
    tiros = estado.tiros_j1 if estado.turno == 1 else estado.tiros_j2
    if tiros >= max_tiros:
        return (ACCION_PLANTARSE,)
    if tiros == 0:
        return (ACCION_TIRAR,)
    return (ACCION_TIRAR, ACCION_PLANTARSE)


def plantarse(estado: Estado) -> Estado:
    if estado.turno == 1:
        return Estado(estado.suma_j1, estado.tiros_j1, estado.suma_j2,
                      estado.tiros_j2, 2, estado.ganador_21)
    if estado.turno == 2:
        return Estado(estado.suma_j1, estado.tiros_j1, estado.suma_j2,
                      estado.tiros_j2, 0, estado.ganador_21)
    raise ValueError("La partida ya ha terminado")


def registrar_resultado(estado: Estado, resultado: int, max_tiros: int) -> Estado:
    if estado.turno == 0:
        raise ValueError("La partida ya ha terminado")

    if resultado == RESULTADO_21:
        return Estado(estado.suma_j1, estado.tiros_j1 + (estado.turno == 1),
                      estado.suma_j2, estado.tiros_j2 + (estado.turno == 2),
                      0, estado.turno)

    if estado.turno == 1:
        tiros = estado.tiros_j1 + 1
        return Estado(resultado, tiros, estado.suma_j2, estado.tiros_j2,
                      2 if tiros >= max_tiros else 1, 0)

    tiros = estado.tiros_j2 + 1
    return Estado(estado.suma_j1, estado.tiros_j1, resultado, tiros,
                  0 if tiros >= max_tiros else 2, 0)


def lanzar_dados() -> tuple[int, int]:
    return randint(1, 6), randint(1, 6)


def ganador(estado: Estado) -> int:
    if estado.turno != 0:
        raise ValueError("Todavia no se puede determinar el ganador")
    if estado.ganador_21:
        return estado.ganador_21
    if estado.suma_j1 > estado.suma_j2:
        return 1
    if estado.suma_j2 > estado.suma_j1:
        return 2
    return 0


def utilidad(estado: Estado) -> int:
    resultado = ganador(estado)
    return 1 if resultado == 1 else -1 if resultado == 2 else 0
