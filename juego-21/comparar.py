"""
comparar.py - Compara Minimax y Alfa-Beta desde el estado inicial.

Para cada cantidad de lanzamientos por jugador, corre los dos algoritmos
y muestra: valor del juego, nodos visitados, podas y tiempo.
Uso:  python comparar.py
"""
import time
from math import inf

import reglas
from minimax import minimax, Contador
from alfaBeta import alfabeta


def correr(metodo, tiros):
    """Ejecuta un algoritmo con 'tiros' lanzamientos por jugador."""
    reglas.maxTiros = tiros        # sucesores() lee este valor de reglas
    estado = ("LANZA_A", None, None, tiros)
    c = Contador()
    t0 = time.perf_counter()
    if metodo == "minimax":
        v = minimax(estado, c)
    else:
        v = alfabeta(estado, -inf, inf, c)
    v = round(v, 10) + 0.0         # evita ver -0.0000 por redondeo de decimales
    return v, c, time.perf_counter() - t0


def comparar(lista_tiros=(1, 2)):
    for tiros in lista_tiros:
        print(f"\n=== {tiros} lanzamiento(s) por jugador ===")
        print(f"{'Método':<10}{'Valor':>9}{'Nodos':>12}{'Podas':>10}{'Tiempo(s)':>12}")
        res = {}
        for metodo in ("minimax", "alfabeta"):
            v, c, t = correr(metodo, tiros)
            res[metodo] = (v, c, t)
            print(f"{metodo:<10}{v:>9.4f}{c.nodos:>12}{c.podas:>10}{t:>12.4f}")

        (v1, c1, t1), (v2, c2, t2) = res["minimax"], res["alfabeta"]
        igual = abs(v1 - v2) < 1e-9
        print(f"Mismo valor en ambos: {'SÍ' if igual else 'NO (revisar)'}")
        print(f"Nodos evitados por Alfa-Beta: {100 * (1 - c2.nodos / c1.nodos):.1f} %")
        print(f"Tiempo ahorrado por Alfa-Beta: {100 * (1 - t2 / t1):.1f} %")
        quien = "A" if v1 > 0 else "B" if v1 < 0 else "nadie (juego parejo)"
        print(f"Valor del juego: {v1:+.4f} (ventaja para {quien})")


if __name__ == "__main__":
    comparar()