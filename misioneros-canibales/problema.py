
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
