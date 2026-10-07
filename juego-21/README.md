# Juego del 21

## El problema

Participan dos jugadores. Cada jugador lanza un cubilete con dos dados. El
objetivo es obtener la combinación **2 y 1** en los dados. Si ninguno la obtiene,
gana la jugada mayor.


## Metodología sugerida

Como el espacio de estados es pequeño (todas las combinaciones de 2 dados), se
puede usar **búsqueda en anchura (BFS)** para recorrer las combinaciones posibles,
y comparar con **búsqueda en profundidad (DFS)**.

> La práctica pide **dos metodologías** para compararlas. Sugerencia: **BFS vs. DFS**.



