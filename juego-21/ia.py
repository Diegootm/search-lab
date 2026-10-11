"""
ia.py - Decisión de la IA: elige PLANTARSE o RELANZAR usando
Minimax o Poda Alfa-Beta sobre el árbol del juego.
"""
import time
from math import inf

from reglas import tipo, sucesores, estadoInicial
from minimax import minimax, Contador
from alfaBeta import alfabeta


def mejor_accion(e, metodo="alfabeta"):
    """
    Elige la mejor acción desde un nodo de decisión (DECIDE_A o DECIDE_B).

    Evalúa cada acción posible con el algoritmo elegido y se queda con la
    que da mejor utilidad esperada para el jugador que decide:
      - A (MAX) busca el valor más alto
      - B (MIN) busca el valor más bajo

    Devuelve: (accion, valor_esperado, nodos, podas, segundos)
    """
    t = tipo(e)
    mejor, val_mejor = None, (-inf if t == "MAX" else inf)
    c = Contador()
    t0 = time.perf_counter()
    for accion, hijo in sucesores(e):
        if metodo == "minimax":
            v = minimax(hijo, c)
        else:
            v = alfabeta(hijo, -inf, inf, c)
        if (t == "MAX" and v > val_mejor) or (t == "MIN" and v < val_mejor):
            mejor, val_mejor = accion, v
    return mejor, val_mejor, c.nodos, c.podas, time.perf_counter() - t0


def comparar_desde_inicio():
    """
    Corre Minimax y Alfa-Beta sobre el árbol completo, desde el estado inicial.
    Devuelve {"minimax": (valor, nodos, podas, segundos),
              "alfabeta": (valor, nodos, podas, segundos)}
    """
    resultado = {}
    for metodo in ("minimax", "alfabeta"):
        c = Contador()
        t0 = time.perf_counter()
        if metodo == "minimax":
            v = minimax(estadoInicial, c)
        else:
            v = alfabeta(estadoInicial, -inf, inf, c)
        resultado[metodo] = (round(v, 10) + 0.0, c.nodos, c.podas,
                             time.perf_counter() - t0)
    return resultado


if __name__ == "__main__":
    # Prueba rápida: lo que decide la IA según su jugada tras el primer lanzamiento
    from reglas import valor, nombre, maxTiros
    print("Decisión de A tras su primer lanzamiento (Alfa-Beta):")
    for d1, d2 in [(6, 5), (5, 3), (4, 1), (3, 2), (2, 1)]:
        s = valor(d1, d2)
        acc, v, nodos, podas, seg = mejor_accion(("DECIDE_A", s, None, maxTiros - 1))
        print(f"  Sacó {nombre(s):>3}: {acc:<9} (valor esperado {v:+.3f}, {nodos} nodos, {seg:.2f} s)")
