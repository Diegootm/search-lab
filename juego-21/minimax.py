"""
minimax.py - Minimax con nodos de azar (Expectiminimax).

Recorre el árbol del juego en profundidad (DFS) y devuelve la utilidad
esperada del estado que se le entrega:
  - nodo MAX  (decide A): el MAYOR valor de sus hijos
  - nodo MIN  (decide B): el MENOR valor de sus hijos
  - nodo AZAR (lanzamiento): el PROMEDIO ponderado (cada resultado 1/36)
"""
from reglas import es_terminal, tipo, sucesores, utilidad, P


class Contador:
    """Cuenta cuántos nodos visitó el algoritmo (y podas, para Alfa-Beta)."""
    def __init__(self):
        self.nodos = 0
        self.podas = 0


def minimax(e, c):
    c.nodos += 1
    if es_terminal(e):                    # caso base: fin de la partida
        return utilidad(e[1], e[2])
    t = tipo(e)
    if t == "MAX":
        return max(minimax(h, c) for _, h in sucesores(e))
    if t == "MIN":
        return min(minimax(h, c) for _, h in sucesores(e))
    # AZAR: valor esperado = suma de probabilidad * valor de cada resultado
    return sum(P * minimax(h, c) for _, h in sucesores(e))


if __name__ == "__main__":
    import time
    from reglas import estadoInicial, maxTiros
    c = Contador()
    t0 = time.perf_counter()
    v = minimax(estadoInicial, c)
    t = time.perf_counter() - t0
    print(f"Lanzamientos por jugador: {maxTiros}")
    print(f"Minimax -> valor {v:.4f} | nodos {c.nodos} | tiempo {t:.2f} s")