"""Comparacion reproducible desde el mismo estado, sin interfaz."""

import argparse

from alfa_beta import BuscadorAlfaBeta
from minimax import BuscadorMinimax
from motor import Estado


def comparar(max_tiros: int = 3) -> None:
    estado = Estado()
    resultados = []
    for nombre, clase in (("Minimax", BuscadorMinimax),
                          ("Alfa-Beta", BuscadorAlfaBeta)):
        decision = clase(max_tiros).elegir_accion(estado)
        e = decision.estadisticas
        resultados.append((nombre, decision.accion, decision.valor,
                           e.nodos, e.nodos_azar, e.podas, e.cache,
                           1000 * e.segundos))

    print(f"Comparacion con MAX_TIROS = {max_tiros}")
    print(f"{'Metodo':<12} {'Accion':<12} {'Valor':>10} {'Estados':>10} "
          f"{'Azar':>8} {'Podas':>8} {'Cache':>8} {'ms':>11}")
    for nombre, accion, valor, nodos, azar, podas, cache, ms in resultados:
        print(f"{nombre:<12} {accion:<12} {valor:>10.6f} {nodos:>10} "
              f"{azar:>8} {podas:>8} {cache:>8} {ms:>11.2f}")

    if (resultados[0][1] != resultados[1][1] or
            abs(resultados[0][2] - resultados[1][2]) > 1e-8):
        raise AssertionError("Las metodologias dieron resultados distintos")
    print("Verificacion: misma accion y utilidad esperada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tiros", type=int, default=3)
    opciones = parser.parse_args()
    if opciones.tiros < 1:
        parser.error("El numero de tiros debe ser al menos 1")
    comparar(opciones.tiros)
