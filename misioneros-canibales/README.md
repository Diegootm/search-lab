# Misioneros y Caníbales

## El problema

Tres misioneros y tres caníbales están en una orilla de un río, con un bote que
puede llevar a una o dos personas. Hay que pasar a todos a la otra orilla **sin
que en ninguna orilla los caníbales superen en número a los misioneros** (porque
se los comerían).


## Metodología sugerida

Este problema se resuelve bien con **búsqueda en anchura (BFS)** porque garantiza
la solución con el menor número de cruces, y con **A*** si se quiere comparar con
una heurística (por ejemplo: número de personas que faltan por cruzar).

> Recuerden que la práctica pide **dos metodologías** por problema para poder
> compararlas con los parámetros de evaluación (completitud, optimidad,
> complejidad temporal y espacial). Sugerencia: **BFS vs. DFS**, o **BFS vs. A***.

