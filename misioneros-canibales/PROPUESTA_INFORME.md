# Informe del proyecto: Misioneros y Caníbales

## I. Introducción

El problema de Misioneros y Caníbales consiste en trasladar a tres misioneros y tres caníbales de una orilla de un río a otra utilizando un bote con capacidad para dos personas, sin incumplir las restricciones de seguridad.

Este proyecto implementa dos algoritmos de búsqueda en Python: BFS (*Breadth-First Search*) y A* (*A-Star*). Mediante una interfaz gráfica desarrollada con Pygame, se pueden visualizar las soluciones, examinar el proceso de búsqueda y comparar métricas como los nodos explorados y el tiempo de ejecución.

## II. Objetivos

### Objetivo general

Implementar y comparar BFS y A* para resolver el problema de Misioneros y Caníbales, evaluando sus soluciones y su desempeño computacional.

### Objetivos específicos

- Representar los estados, las acciones y las restricciones del problema.
- Implementar BFS y A* para encontrar una solución válida.
- Aplicar heurísticas para orientar la búsqueda de A*.
- Desarrollar una interfaz gráfica para visualizar las soluciones.
- Comparar los algoritmos mediante métricas de búsqueda y tiempo de ejecución.

## III. Marco teórico

### 3.1. Búsqueda en anchura (BFS)

BFS es un algoritmo de búsqueda no informada que explora los estados por niveles mediante una cola FIFO. Primero procesa los estados más cercanos al inicial y después continúa con los siguientes niveles.

En este problema, cada acción representa un cruce del río. Como cada cruce tiene un costo de 1, BFS encuentra una solución con el menor número de cruces si la implementación controla correctamente los estados repetidos.

Su complejidad general en grafos es \(O(V+E)\), donde \(V\) representa los estados y \(E\) las transiciones.

### 3.2. Búsqueda A*

A* es un algoritmo de búsqueda informada que utiliza una función heurística para orientar la exploración hacia el objetivo. Su función de evaluación es:

`f(n) = g(n) + h(n)`

- `g(n)`: costo acumulado desde el inicio.
- `h(n)`: estimación del costo restante.
- `f(n)`: costo estimado de la solución que pasa por el nodo.

El proyecto incluye dos heurísticas:

- `h_personas(estado)`: cuenta las personas que permanecen en la orilla izquierda. No es admisible en general.
- `h_cruces_minimos(estado)`: estima los cruces restantes y está diseñada para ser admisible y consistente.

La segunda es la opción apropiada para evaluar A* con garantía de optimalidad, bajo las condiciones necesarias de implementación.

## IV. Ingeniería

### 4.1. Descripción y abstracción del problema

El objetivo es trasladar a todos los personajes a la orilla derecha respetando estas reglas:

- El bote transporta una o dos personas.
- No puede cruzar vacío.
- Los pasajeros deben estar en la orilla de salida.
- En ninguna orilla puede haber más caníbales que misioneros si hay misioneros presentes.
- Cada cruce tiene un costo de 1.

El estado se representa como `(M, C, B)`, donde `M` y `C` son las cantidades de misioneros y caníbales en la orilla izquierda, y `B` indica la posición del bote (`1` izquierda, `0` derecha).

- Estado inicial: `(3, 3, 1)`.
- Estado objetivo: `(0, 0, 0)`.

Las acciones posibles son transportar uno o dos misioneros, uno o dos caníbales, o un misionero y un caníbal. El programa valida cada transición antes de aceptar el nuevo estado.

La interfaz y las animaciones permiten visualizar el problema, pero no forman parte del estado utilizado por los algoritmos.

### 4.2. Formulación de la meta

La meta consiste en encontrar una secuencia de cruces válidos que lleve del estado inicial al objetivo con el menor costo posible.

BFS explora por niveles, mientras que A* prioriza los estados mediante `g(n) + h(n)`. Ambos buscan una solución válida; A* utiliza una heurística para orientar la exploración.

### 4.3. REAS

| Elemento | Descripción |
|---|---|
| **Rendimiento** | Alcanzar el objetivo, respetar las reglas y minimizar los cruces. |
| **Entorno** | Río, dos orillas, seis personajes y un bote. |
| **Actuadores** | Ejecutar cruces con pasajeros permitidos. |
| **Sensores** | Consultar el estado, la posición del bote y los sucesores válidos. |

El entorno es discreto, observable, determinista y secuencial.

### 4.4. Conjunto problema

Una representación formal es:

`P = (S, s0, A, T, G, c)`

| Componente | Descripción |
|---|---|
| `S` | Estados representados por `(M, C, B)`. |
| `s0` | Estado inicial `(3, 3, 1)`. |
| `A` | Combinaciones válidas de pasajeros. |
| `T` | Transiciones que calculan los nuevos estados. |
| `G` | Estado objetivo `(0, 0, 0)`. |
| `c` | Costo unitario por cruce. |

### 4.5. Tecnologías y módulos

| Archivo o tecnología | Función |
|---|---|
| Python | Implementación de la lógica y los algoritmos. |
| Pygame | Interfaz gráfica y animaciones. |
| `problema.py` | Estados, acciones, validaciones y heurísticas. |
| `busqueda.py` | Algoritmos BFS y A*. |
| `metricas.py` | Medición y presentación de resultados. |
| `comparar.py` | Comparación de los algoritmos desde consola. |
| `interfaz.py` | Visualización e interacción con el usuario. |
| `main.py` | Inicio de la aplicación. |
| `README.md` | Documentación e instrucciones. |

### 4.6. Prototipo y evidencias

El prototipo permite resolver el problema, visualizar la ruta y consultar información sobre el proceso de búsqueda.

Para documentarlo, incluyan capturas reales de:

1. La pantalla principal y la selección del algoritmo.
2. La representación de los personajes y el bote.
3. Una ruta solución obtenida por BFS o A*.
4. La traza de búsqueda, si se utiliza.
5. La comparación de métricas desde `comparar.py`.
6. El estado final con todos los personajes en la orilla derecha.

### 4.7. Evaluación comparativa

La comparación debe realizarse con el mismo estado inicial y las mismas reglas.

| Métrica | BFS | A* |
|---|---|---|
| ¿Encontró solución? | Por medir | Por medir |
| Número de cruces | Por medir | Por medir |
| Nodos generados | Por medir | Por medir |
| Nodos expandidos | Por medir | Por medir |
| Tiempo de ejecución | Por medir | Por medir |
| Memoria utilizada | Si se mide | Si se mide |

Para obtener resultados más fiables, repitan las ejecuciones y calculen el promedio o la mediana del tiempo.

BFS encuentra una solución de costo mínimo cuando todos los cruces tienen el mismo costo. A* puede reducir la exploración mediante su heurística, pero su eficiencia real debe comprobarse con las mediciones. No debe afirmarse que siempre es más rápido.

### 4.8. Limitaciones

- El problema utiliza tres misioneros, tres caníbales y un bote con capacidad para dos personas.
- La heurística de personas no garantiza optimalidad.
- El rendimiento depende de la implementación, la heurística y el equipo utilizado.
- Los nodos generados y expandidos son métricas diferentes.
- La memoria y la profundidad solo deben reportarse si se miden realmente.
- Las animaciones no deben incluirse en el tiempo de búsqueda si se quiere medir únicamente el algoritmo.

## V. Conclusiones

Las conclusiones deben basarse en las ejecuciones realizadas. Se debe analizar si ambos algoritmos encontraron soluciones válidas, si obtuvieron el mismo costo y qué diferencias presentaron en los nodos explorados y el tiempo de ejecución.

También debe explicarse cómo influye la heurística en A* y distinguir entre las propiedades teóricas de los algoritmos y los resultados observados. No debe afirmarse que A* es siempre superior a BFS a partir de una sola prueba.

## VI. Referencias bibliográficas

- Russell, S. J., y Norvig, P. *Artificial Intelligence: A Modern Approach*. Indicar la edición, el año y las páginas consultadas.
- Python Software Foundation. https://docs.python.org/3/
- Pygame Documentation. https://www.pygame.org/docs/

Incluir únicamente las fuentes consultadas durante el desarrollo del proyecto.