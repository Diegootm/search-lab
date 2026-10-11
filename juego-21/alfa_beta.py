"""
alfa_beta.py - Poda Alfa-Beta para Expectiminimax.

Devuelve el MISMO valor que Minimax, pero evita visitar ramas que no
pueden cambiar la decisión final.
  alfa = mejor valor que MAX ya tiene asegurado en el camino actual
  beta = mejor valor que MIN ya tiene asegurado en el camino actual
Si en algún momento alfa >= beta, el resto de hijos se descarta (poda).
"""
from math import inf
from reglas import es_terminal, tipo, sucesores, utilidad, P, utilidadMax, utilidadMin
from minimax import Contador


def alfabeta(e, alfa, beta, c):
    c.nodos += 1
    if es_terminal(e):
        return utilidad(e[1], e[2])
    t = tipo(e)
    hijos = sucesores(e)

    if t == "MAX":
        v = -inf
        for _, h in hijos:
            v = max(v, alfabeta(h, alfa, beta, c))
            if v >= beta:                 # MIN no dejaría llegar aquí: poda
                c.podas += 1
                return v
            alfa = max(alfa, v)
        return v

    if t == "MIN":
        v = inf
        for _, h in hijos:
            v = min(v, alfabeta(h, alfa, beta, c))
            if v <= alfa:                 # MAX no dejaría llegar aquí: poda
                c.podas += 1
                return v
            beta = min(beta, v)
        return v

    # AZAR: no se puede podar como en MAX/MIN porque el valor es un promedio.
    # Se acota lo que falta por explorar suponiendo lo peor (utilidadMin) y lo
    # mejor (utilidadMax) para los resultados todavía no visitados.
    acum, resto = 0.0, 1.0        # acum = suma ya calculada; resto = prob. sin visitar
    for _, h in hijos:
        resto -= P
        # ventana que debe cumplir ESTE hijo para que el promedio importe
        a_h = max(utilidadMin, (alfa - acum - resto * utilidadMax) / P)
        b_h = min(utilidadMax, (beta - acum - resto * utilidadMin) / P)
        v = alfabeta(h, a_h, b_h, c)
        acum += P * v
        if acum + resto * utilidadMin >= beta - 1e-12:   # ni en el peor caso baja de beta
            c.podas += 1
            return acum + resto * utilidadMin
        if acum + resto * utilidadMax <= alfa + 1e-12:   # ni en el mejor caso supera alfa
            c.podas += 1
            return acum + resto * utilidadMax
    return acum


if __name__ == "__main__":
    import time
    from reglas import estadoInicial, maxTiros
    c = Contador()
    t0 = time.perf_counter()
    v = alfabeta(estadoInicial, -inf, inf, c)
    t = time.perf_counter() - t0
    print(f"Lanzamientos por jugador: {maxTiros}")
    print(f"Alfa-Beta -> valor {v:.4f} | nodos {c.nodos} | podas {c.podas} | tiempo {t:.2f} s")