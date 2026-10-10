"""Reglas del Juego del 21, independientes del algoritmo de busqueda."""

from collections import Counter
from dataclasses import dataclass, replace
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
    terminado_j1: bool = False
    terminado_j2: bool = False


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
    """Cuenta las 36 parejas de dados y calcula la probabilidad de cada resultado."""
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
    """Reconoce el 2 y 1 especial; en los otros casos suma los dados."""
    if {dado_1, dado_2} == {1, 2}:
        return RESULTADO_21
    return dado_1 + dado_2


DISTRIBUCION = crear_distribucion()


def acciones_disponibles(estado: Estado, max_tiros: int) -> tuple[str, ...]:
    """Permite el primer tiro obligatorio y luego tirar o plantarse segun el limite."""
    if estado.turno == 0:
        return ()
    tiros = estado.tiros_j1 if estado.turno == 1 else estado.tiros_j2
    if tiros >= max_tiros:
        return (ACCION_PLANTARSE,)
    if tiros == 0:
        return (ACCION_TIRAR,)
    return (ACCION_TIRAR, ACCION_PLANTARSE)


def siguiente_turno(estado: Estado, jugador: int) -> int:
    """Pasa al rival si puede jugar; termina cuando ambos se retiraron."""
    rival = 3 - jugador
    finalizados = {1: estado.terminado_j1, 2: estado.terminado_j2}
    if not finalizados[rival]:
        return rival
    return 0 if finalizados[jugador] else jugador


def plantarse(estado: Estado) -> Estado:
    """Conserva la puntuacion y retira al jugador durante toda la ronda."""
    if estado.turno not in (1, 2):
        raise ValueError("La partida ya ha terminado")
    tiros = estado.tiros_j1 if estado.turno == 1 else estado.tiros_j2
    if tiros == 0:
        raise ValueError("Debes lanzar al menos una vez antes de plantarte")
    nuevo = replace(estado, **{f"terminado_j{estado.turno}": True})
    return replace(nuevo, turno=siguiente_turno(nuevo, estado.turno))


def registrar_resultado(estado: Estado, resultado: int, max_tiros: int) -> Estado:
    """Guarda la ultima tirada y entrega el turno al siguiente jugador disponible."""
    if ACCION_TIRAR not in acciones_disponibles(estado, max_tiros):
        raise ValueError("No se puede lanzar en este estado")
    jugador = estado.turno
    tiros = (estado.tiros_j1 if jugador == 1 else estado.tiros_j2) + 1
    cambios = {f"tiros_j{jugador}": tiros}
    if resultado == RESULTADO_21:
        return replace(estado, **cambios, turno=0, ganador_21=jugador)
    if resultado not in range(2, 13):
        raise ValueError("El resultado debe ser una suma de dos dados o el 21 especial")
    cambios[f"suma_j{jugador}"] = resultado
    cambios[f"terminado_j{jugador}"] = tiros >= max_tiros
    nuevo = replace(estado, **cambios)
    return replace(nuevo, turno=siguiente_turno(nuevo, jugador))


def lanzar_dados() -> tuple[int, int]:
    """Genera al azar un valor entre uno y seis para cada dado."""
    return randint(1, 6), randint(1, 6)


def ganador(estado: Estado) -> int:
    """Compara las puntuaciones al terminar o devuelve al ganador del 2 y 1."""
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
    """Expresa el resultado desde J1: ganar vale 1, perder -1 y empatar 0."""
    resultado = ganador(estado)
    return 1 if resultado == 1 else -1 if resultado == 2 else 0
