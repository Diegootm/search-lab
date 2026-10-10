"""Expectiminimax exacto: MAX, MIN y nodos de azar."""

from time import perf_counter

from motor import (
    ACCION_PLANTARSE, ACCION_TIRAR, DISTRIBUCION, Decision,
    Estado, Estadisticas, acciones_disponibles, plantarse,
    registrar_resultado, utilidad,
)


class BuscadorMinimax:
    def __init__(self, max_tiros: int):
        """Prepara los datos y recursos que necesita este objeto."""
        self.max_tiros = max_tiros
        self.estadisticas = Estadisticas()
        self.valores_exacto: dict[Estado, float] = {}

    def evaluar_estado(self, estado: Estado) -> float:
        """Reutiliza estados conocidos y busca lo mejor para el jugador que tiene el turno."""
        if estado in self.valores_exacto:
            self.estadisticas.cache += 1
            return self.valores_exacto[estado]

        self.estadisticas.nodos += 1
        if estado.turno == 0:
            self.estadisticas.hojas += 1
            valor = float(utilidad(estado))
        else:
            valores = [self.evaluar_accion(estado, accion)
                       for accion in acciones_disponibles(estado, self.max_tiros)]
            valor = max(valores) if estado.turno == 1 else min(valores)

        self.valores_exacto[estado] = valor
        return valor

    def evaluar_accion(self, estado: Estado, accion: str) -> float:
        """Evalua plantarse o combina los resultados de tirar segun sus probabilidades."""
        if accion == ACCION_PLANTARSE:
            return self.evaluar_estado(plantarse(estado))
        if accion != ACCION_TIRAR:
            raise ValueError(f"Accion desconocida: {accion}")

        self.estadisticas.nodos_azar += 1
        esperado = 0.0
        for resultado, probabilidad in DISTRIBUCION:
            siguiente = registrar_resultado(estado, resultado, self.max_tiros)
            esperado += probabilidad * self.evaluar_estado(siguiente)
        return esperado

    def elegir_accion(self, estado: Estado) -> Decision:
        """Compara las acciones legales y elige la mejor para el jugador actual."""
        if estado.turno == 0:
            raise ValueError("No hay decisiones en un estado terminal")

        inicio = perf_counter()
        opciones = acciones_disponibles(estado, self.max_tiros)
        mejor_accion = opciones[0]
        mejor_valor = self.evaluar_accion(estado, mejor_accion)
        for accion in opciones[1:]:
            valor = self.evaluar_accion(estado, accion)
            if (estado.turno == 1 and valor > mejor_valor + 1e-12) or (
                estado.turno == 2 and valor < mejor_valor - 1e-12
            ):
                mejor_accion, mejor_valor = accion, valor

        self.estadisticas.segundos = perf_counter() - inicio
        return Decision(mejor_accion, mejor_valor, self.estadisticas)
