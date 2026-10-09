
"""Formulación del problema de los Misioneros y los Caníbales.

Representación del estado
-------------------------
Un estado es la tupla ``(M, C, B)`` donde:

* ``M`` = número de misioneros en la orilla IZQUIERDA (0..3)
* ``C`` = número de caníbales en la orilla IZQUIERDA (0..3)
* ``B`` = posición del bote: 1 si está en la orilla izquierda, 0 si está en la derecha

La orilla derecha se deduce: ``(N - M, N - C)``.

* Estado inicial:  (3, 3, 1)  -> todos y el bote en la orilla izquierda
* Estado objetivo: (0, 0, 0)  -> todos y el bote en la orilla derecha

Operadores (acciones)
---------------------
El bote lleva 1 o 2 personas. Cada acción es ``(m, c)`` = misioneros y caníbales
que viajan en el bote. Se aplican en la dirección en la que esté el bote.

Restricción
-----------
En ninguna orilla los caníbales pueden superar a los misioneros, salvo que en esa
orilla no haya misioneros (no hay a quién comerse).

Costo
-----
Cada cruce del río cuesta 1, por lo que el costo de la ruta = número de cruces.
"""

from __future__ import annotations

from typing import NamedTuple

N_MISIONEROS = 3
N_CANIBALES = 3
CAPACIDAD_BOTE = 2

IZQUIERDA = 1
DERECHA = 0



class Estado(NamedTuple):
    m: int  # misioneros en la orilla izquierda
    c: int  # caníbales en la orilla izquierda
    b: int  # 1 = bote a la izquierda, 0 = bote a la derecha

    def __str__(self) -> str:
        return f"({self.m}, {self.c}, {self.b})"

    @property
    def derecha(self) -> tuple[int, int]:
        """(misioneros, caníbales) en la orilla derecha."""
        return N_MISIONEROS - self.m, N_CANIBALES - self.c



ESTADO_INICIAL = Estado(N_MISIONEROS, N_CANIBALES, IZQUIERDA)
ESTADO_OBJETIVO = Estado(0, 0, DERECHA)

# Operadores: (misioneros en el bote, caníbales en el bote)
ACCIONES: tuple[tuple[int, int], ...] = ((1, 0), (2, 0), (0, 1), (0, 2), (1, 1))

COSTO_CRUCE = 1



def nombre_accion(accion: tuple[int, int]) -> str:
    """Texto legible de un operador, p. ej. (1, 1) -> '1M 1C'."""
    m, c = accion
    partes = []
    if m:
        partes.append(f"{m}M")
    if c:
        partes.append(f"{c}C")
    return " ".join(partes)


def describir_movimiento(accion: tuple[int, int], origen: Estado) -> str:
    """Descripción completa del movimiento, indicando la dirección del cruce."""
    m, c = accion
    quienes = []
    if m:
        quienes.append(f"{m} misionero{'s' if m > 1 else ''}")
    if c:
        quienes.append(f"{c} caníbal{'es' if c > 1 else ''}")
    direccion = "izq → der" if origen.b == IZQUIERDA else "der → izq"
    verbo = "Cruza" if m + c == 1 else "Cruzan"
    return f"{verbo} {' y '.join(quienes)} ({direccion})"



def en_rango(estado: Estado) -> bool:
    """Comprueba que las cantidades y la posición del bote sean válidas."""
    return 0 <= estado.m <= N_MISIONEROS and 0 <= estado.c <= N_CANIBALES and estado.b in (0, 1)


def orilla_segura(misioneros: int, canibales: int) -> bool:
    """La orilla es segura si no hay misioneros o no son superados."""
    return misioneros == 0 or misioneros >= canibales



def es_valido(estado: Estado) -> bool:
    """Estado válido: dentro de rango y con ambas orillas seguras."""
    if not en_rango(estado):
        return False
    m_der, c_der = estado.derecha
    return orilla_segura(estado.m, estado.c) and orilla_segura(m_der, c_der)


def motivo_invalidez(estado: Estado) -> str | None:
    """Explica por qué un estado es inválido (``None`` si es válido)."""
    if not en_rango(estado):
        return "no hay suficientes personas en la orilla de partida"
    m_der, c_der = estado.derecha
    if not orilla_segura(estado.m, estado.c):
        return f"orilla izquierda: {estado.c}C > {estado.m}M"
    if not orilla_segura(m_der, c_der):
        return f"orilla derecha: {c_der}C > {m_der}M"
    return None
