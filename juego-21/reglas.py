# Reglas del juego 21 
"""
reglas.py - Reglas del Juego 21 (sin ningún algoritmo de búsqueda).
"""

import itertools

maxTiros = 2    
utilidadMax, utilidadMin = 1.0, -1.0                  
RESULTADOS = list(itertools.product(range(1, 7), repeat=2))
P = 1 / 36

def valor(d1, d2):
    if {d1, d2} == {1, 2}:
        return 1000                        
    if d1 == d2:
        return 100 + d1                    
    return max(d1, d2) * 10 + min(d1, d2)  


def nombre(resultado):
    if resultado == 1000:
        return "21"
    if 101 <= resultado <= 106:
        return f"doble {resultado - 100}"
    return str(resultado)


def utilidad(sA, sB):
    return 1 if sA > sB else (-1 if sA < sB else 0)


estadoInicial = ("LANZA_A", None, None, maxTiros)


def es_terminal(e):
    return e[0] == "FIN"


def tipo(e):
    return {"LANZA_A": "AZAR", "LANZA_B": "AZAR",
            "DECIDE_A": "MAX", "DECIDE_B": "MIN"}[e[0]]


def sucesores(e):
    """Devuelve lista de (accion, estado_hijo). Para AZAR, accion = jugada."""
    fase, sA, sB, r = e
    if fase == "LANZA_A":
        return [((d1, d2), ("DECIDE_A", valor(d1, d2), None, r - 1))
                for d1, d2 in RESULTADOS]
    if fase == "LANZA_B":
        return [((d1, d2), ("DECIDE_B", sA, valor(d1, d2), r - 1))
                for d1, d2 in RESULTADOS]
    if fase == "DECIDE_A":
        hijos = [("plantarse", ("LANZA_B", sA, None, maxTiros))]
        if r > 0:
            hijos.append(("relanzar", ("LANZA_A", None, None, r)))
        return hijos
    if fase == "DECIDE_B":
        hijos = [("plantarse", ("FIN", sA, sB, 0))]
        if r > 0:
            hijos.append(("relanzar", ("LANZA_B", sA, None, r)))
        return hijos


if __name__ == "__main__":
    assert valor(2, 1) == valor(1, 2) == 1000
    assert valor(6, 6) == 106 and valor(1, 1) == 101
    assert valor(6, 5) == valor(5, 6) == 65
    assert valor(6, 6) > valor(6, 5) and valor(1, 1) > valor(6, 5)
    assert valor(2, 1) > valor(6, 6)
    assert utilidad(65, 43) == 1 and utilidad(43, 65) == -1 and utilidad(65, 65) == 0
    assert len(RESULTADOS) == 36
    assert len(sucesores(estadoInicial)) == 36
    assert tipo(estadoInicial) == "AZAR"
    print("reglas.py: todas las pruebas pasaron")
    for d1, d2 in [(2, 1), (6, 6), (1, 1), (6, 5), (3, 1)]:
        print(f"  dados {d1} y {d2} -> {valor(d1, d2):>4}  ({nombre(valor(d1, d2))})")