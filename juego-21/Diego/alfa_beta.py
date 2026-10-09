"""Expectiminimax con alfa-beta y limites seguros en nodos de azar (Star1)."""

from math import inf
from time import perf_counter

from motor import (
    ACCION_PLANTARSE, ACCION_TIRAR, DISTRIBUCION, Decision,
    Estado, Estadisticas, acciones_disponibles, plantarse,
    registrar_resultado, utilidad,
)


class BuscadorAlfaBeta:
    def __init__(self, max_tiros: int):
        self.max_tiros = max_tiros
        self.estadisticas = Estadisticas()
        self.valores_exacto: dict[Estado, float] = {}

    def evaluar_estado(self, estado: Estado, alfa: float = -inf,
                       beta: float = inf) -> float:
        if estado in self.valores_exacto:
            self.estadisticas.cache += 1
            return self.valores_exacto[estado]

        self.estadisticas.nodos += 1
        if estado.turno == 0:
            self.estadisticas.hojas += 1
            valor = float(utilidad(estado))
            self.valores_exacto[estado] = valor
            return valor

        opciones = acciones_disponibles(estado, self.max_tiros)
        ventana_completa = alfa <= -1.0 and beta >= 1.0

        if estado.turno == 1:
            mejor = -inf
            for indice, accion in enumerate(opciones):
                valor = self.evaluar_accion(estado, accion, alfa, beta)
                mejor = max(mejor, valor)
                if mejor >= beta:
                    self.estadisticas.podas += len(opciones) - indice - 1
                    if ventana_completa:
                        self.valores_exacto[estado] = 1.0
                    return beta
                alfa = max(alfa, mejor)
            resultado = alfa
        else:
            mejor = inf
            for indice, accion in enumerate(opciones):
                valor = self.evaluar_accion(estado, accion, alfa, beta)
                mejor = min(mejor, valor)
                if mejor <= alfa:
                    self.estadisticas.podas += len(opciones) - indice - 1
                    if ventana_completa:
                        self.valores_exacto[estado] = -1.0
                    return alfa
                beta = min(beta, mejor)
            resultado = beta

        if ventana_completa:
            self.valores_exacto[estado] = resultado
        return resultado

    def evaluar_accion(self, estado: Estado, accion: str,
                       alfa: float, beta: float) -> float:
        if accion == ACCION_PLANTARSE:
            return self.evaluar_estado(plantarse(estado), alfa, beta)
        if accion != ACCION_TIRAR:
            raise ValueError(f"Accion desconocida: {accion}")

        self.estadisticas.nodos_azar += 1
        suma_ponderada = 0.0
        peso_restante = 36

        for indice, (resultado, probabilidad) in enumerate(DISTRIBUCION):
            peso = round(probabilidad * 36)
            peso_restante -= peso

            alfa_hijo = (36 * alfa - suma_ponderada - peso_restante) / peso
            beta_hijo = (36 * beta - suma_ponderada + peso_restante) / peso

            if alfa_hijo >= 1.0:
                self.estadisticas.podas += len(DISTRIBUCION) - indice
                return alfa
            if beta_hijo <= -1.0:
                self.estadisticas.podas += len(DISTRIBUCION) - indice
                return beta

            siguiente = registrar_resultado(estado, resultado, self.max_tiros)
            valor = self.evaluar_estado(
                siguiente, max(-1.0, alfa_hijo), min(1.0, beta_hijo)
            )

            if valor <= alfa_hijo:
                self.estadisticas.podas += len(DISTRIBUCION) - indice - 1
                return alfa
            if valor >= beta_hijo:
                self.estadisticas.podas += len(DISTRIBUCION) - indice - 1
                return beta

            suma_ponderada += peso * valor

        return suma_ponderada / 36

    def elegir_accion(self, estado: Estado) -> Decision:
        if estado.turno == 0:
            raise ValueError("No hay decisiones en un estado terminal")

        inicio = perf_counter()
        opciones = acciones_disponibles(estado, self.max_tiros)
        mejor_accion = opciones[0]
        mejor_valor = self.evaluar_accion(estado, mejor_accion, -inf, inf)
        alfa, beta = -inf, inf

        if estado.turno == 1:
            alfa = mejor_valor
        else:
            beta = mejor_valor

        for accion in opciones[1:]:
            valor = self.evaluar_accion(estado, accion, alfa, beta)
            if (estado.turno == 1 and valor > mejor_valor + 1e-12) or (
                estado.turno == 2 and valor < mejor_valor - 1e-12
            ):
                mejor_accion, mejor_valor = accion, valor
            if estado.turno == 1:
                alfa = max(alfa, mejor_valor)
            else:
                beta = min(beta, mejor_valor)

        self.estadisticas.segundos = perf_counter() - inicio
        return Decision(mejor_accion, mejor_valor, self.estadisticas)
