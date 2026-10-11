# Propuesta para el informe del Juego 21

Este documento sugiere qué escribir en cada sección según el código actual. Completen los resultados con ejecuciones y capturas propias; no presenten las cifras o conclusiones esperadas como mediciones realizadas.

## I. Introducción

Presenten el Juego 21 como un problema de toma de decisiones entre dos contrincantes con resultados aleatorios. Cada jugador puede conservar su jugada o arriesgarse a reemplazarla mediante otro lanzamiento de dos dados. El prototipo muestra cómo una IA compara esas alternativas mediante búsqueda.

Texto de partida sugerido:

> El proyecto implementa un juego de dos jugadores en el que las decisiones de plantarse o relanzar se resuelven mediante búsqueda adversaria con incertidumbre. Se desarrolló un prototipo en Python con una interfaz Pygame y se compararon Expectiminimax y una variante con poda Alfa-Beta, considerando la utilidad esperada, los nodos visitados y el tiempo de cálculo.

Aclaren que el nombre Minimax en la pantalla corresponde a una implementación con nodos de azar. El proyecto no implementa BFS y DFS como metodologías comparadas, aunque el README original las sugiera.

## II. Objetivos

**Objetivo general sugerido:** implementar y evaluar dos metodologías de búsqueda adversaria con azar para decidir entre plantarse y relanzar en el Juego 21.

**Objetivos específicos sugeridos:**

- Representar las reglas mediante estados, acciones, transiciones y una función de utilidad.
- Implementar Expectiminimax para evaluar las acciones por su utilidad esperada.
- Implementar una variante con poda Alfa-Beta y límites para nodos de azar.
- Construir una interfaz que permita jugar y observar decisiones y métricas.
- Comparar los métodos desde estados idénticos y verificar la coincidencia de sus valores y decisiones en los casos evaluados.

## III. Marco teórico

Dedicar como máximo una plana a cada metodología. En cada una incluir concepto, funcionamiento, aplicación al juego y una referencia bibliográfica verificable. Pueden consultar el capítulo de búsqueda adversaria de *Artificial Intelligence: A Modern Approach*, de Russell y Norvig; indiquen la edición y las páginas que realmente usen.

### Metodología 1: Minimax con azar, o Expectiminimax

Expliquen los nodos MAX, MIN, AZAR y terminales. A maximiza la utilidad; B la minimiza. Los lanzamientos son nodos AZAR con 36 resultados ordenados equiprobables.

Incluyan la regla de evaluación:

```text
V(s) = U(s)                           si s es terminal
V(s) = máximo V(hijo)                 si s es MAX
V(s) = mínimo V(hijo)                 si s es MIN
V(s) = suma P(resultado) × V(hijo)    si s es AZAR
```

Relacionen la explicación con `minimax.py`. El recorrido es recursivo en profundidad, pero DFS es la forma de recorrer el árbol, no una tercera metodología evaluada. El límite de tiros hace finito el árbol.

### Metodología 2: Expectiminimax con poda Alfa-Beta

Expliquen alfa, beta y los cortes en MAX/MIN. Luego describan por qué los nodos AZAR requieren acotar el promedio de resultados pendientes usando el intervalo de utilidad [−1, +1]. Relacionen esa explicación con `alfaBeta.py`.

Formulen la expectativa de evaluación: conservar la utilidad de referencia reduciendo exploración cuando los límites lo permitan. Su magnitud y el ahorro de tiempo deben demostrarse con las mediciones. No afirmen que Alfa-Beta siempre es más rápido ni que aplicar poda convencional a un promedio es suficiente.

## IV. Ingeniería

### 1. Descripción, ampliación y abstracción del problema

Describan dos jugadores, dos dados y hasta `maxTiros` lanzamientos por jugador, actualmente 2. A juega primero y completa su jugada; después B juega conociendo la jugada final de A.

Las reglas implementadas son:

- El 2 y 1, en cualquier orden, es la jugada máxima.
- Le siguen los dobles, desde 66 hasta 11.
- Luego las parejas no dobles, ordenadas por el dado mayor y después el menor.
- Relanzar reemplaza la jugada; plantarse la conserva.
- Al terminar ambos se comparan sus jugadas; una igualdad produce empate.

Expliquen la abstracción: animación, dibujos y tiempo de espera no forman parte del estado de búsqueda. El árbol necesita solamente la fase, las jugadas y los tiros restantes.

### 2. Formulación de la meta

**Meta de la partida:** obtener una jugada superior a la del rival al finalizar.

**Meta del agente:** escoger la acción que optimiza la utilidad esperada desde el estado observado. Para A, maximizarla; para B, minimizarla porque la utilidad se expresa desde A.

Aclaren que una decisión óptima según el modelo no garantiza ganar una partida concreta: los dados introducen azar.

### 3. Formulación del problema: REAS, P → A y conjunto problema

#### REAS

| Elemento | Propuesta según el prototipo |
|---|---|
| Rendimiento | Utilidad final (+1, 0, −1), utilidad esperada de las acciones y esfuerzo de búsqueda medido por nodos y tiempo. |
| Entorno | Dos jugadores, dos dados de seis caras, ranking de jugadas, orden A → B y límite de lanzamientos. |
| Actuadores | Elegir `plantarse` o `relanzar`; la interfaz ejecuta la acción. |
| Sensores | Fase de decisión, jugada propia, jugada final de A cuando decide B y tiros restantes. |

Como caracterización del entorno pueden explicar que es competitivo, estocástico, secuencial y discreto. El estado relevante está disponible para el agente; los resultados futuros de los dados permanecen inciertos.

#### Percepciones → acciones

```text
P = (fase, jugada_A, jugada_B, tiros_restantes)
A = {plantarse, relanzar}, cuando quedan tiros
A = {plantarse}, cuando se agotaron
f(P) = acción elegida por mejor_accion(P, método)
```

Ejemplo sugerido: B percibe que A tiene 65, que su propia jugada es 43 y que le queda un tiro. La IA compara conservar 43 con la esperanza de obtener otra jugada.

El lanzamiento no es una elección de los valores de los dados: sus 36 resultados son sucesores aleatorios.

#### Conjunto problema

Usen la notación solicitada por su docente. Una representación posible es `(S, s0, A, T, G, U)`:

| Componente | Representación en el código |
|---|---|
| S: estados | Tuplas `(fase, sA, sB, r)` con fases `LANZA_A`, `DECIDE_A`, `LANZA_B`, `DECIDE_B` y `FIN`. |
| s0: estado inicial | `("LANZA_A", None, None, maxTiros)`. |
| A: acciones | Plantarse y, si quedan tiros, relanzar. |
| T: transiciones | `sucesores` genera cambios deterministas por decisiones y resultados de lanzamiento con probabilidad 1/36. |
| G: estados terminales | Los estados cuya fase es `FIN`, después de que ambos conservan su jugada. |
| U: evaluación terminal | `utilidad(sA, sB)`: +1 para victoria de A, −1 para victoria de B, 0 para empate. |

Aquí no se minimiza la distancia a una meta como en un laberinto. Si les piden costo de camino, indiquen que no está implementado como criterio de decisión; los lanzamientos consumidos limitan el árbol y la utilidad define la calidad del resultado.

### 4. Tecnologías utilizadas

| Tecnología | Uso real |
|---|---|
| Python | Reglas, representación de estados y algoritmos recursivos. |
| Pygame | Ventana, eventos, botones, textos y animación. |
| `itertools` | Generación de las 36 parejas ordenadas de dados. |
| `random` | Selección de dados reales y efectos visuales de la animación. |
| `math` | Límites infinitos y operaciones de dibujo y movimiento. |
| `time.perf_counter` | Medición del tiempo de búsqueda. |
| `threading` | Comparación inicial en segundo plano mientras se muestra el menú. |

Registren la versión de Python, Pygame, sistema operativo y características del equipo usado para medir. No agreguen librerías que no aparecen en el proyecto.

### 5. Prototipo con dos metodologías y resultados

Describan la separación de módulos: `reglas.py` modela el problema; `minimax.py` y `alfaBeta.py` evalúan; `ia.py` decide; `interfaz.py` coordina; `dibujos.py` representa; `comparar.py` mide.

Incluyan capturas reales con pie de figura:

1. **Menú:** modos humano/IA y elección de algoritmo. Expliquen cómo se configura la partida.
2. **Partida:** jugadas de A y B, tiros usados y mesa. Expliquen el ranking y el estado visible.
3. **Decisión de IA:** registro con acción, utilidad, nodos, podas y tiempo. Identifiquen el estado que produjo la decisión.
4. **Final:** ganador o empate y comparación entre métodos. Distingan resultados de esta partida y evaluación desde el estado inicial.
5. **Consola:** salida de `python comparar.py` para uno y dos tiros. Sirve como evidencia repetible de evaluación desde estados iguales.

El prototipo calcula ambos métodos en cada decisión de IA, pero juega solamente el seleccionado. La comparación desde el inicio es independiente de los dados observados en la partida. Si aparece “calculando”, esperen a que termine antes de capturar las métricas.

### 6. Evaluación comparativa de rutas solución y parámetros de búsqueda

En este juego, una ruta observada es la secuencia de decisiones y resultados de dados de una partida. El algoritmo evalúa una estrategia sobre futuros posibles; no devuelve una ruta única garantizada como un buscador de caminos.

Para comparar decisiones, apliquen ambos métodos al **mismo estado**. No atribuyan al algoritmo una victoria obtenida con dados diferentes. Presenten dos análisis separados: árbol desde el inicio y decisiones observadas durante una partida.

Tabla sugerida para llenar con resultados reales:

| Estado / tiros | Método | Acción, si corresponde | Utilidad esperada | Nodos visitados | Eventos de poda | Tiempo (ms) |
|---|---|---|---|---|---|---|
| Inicial / 1 | Minimax | No aplica: comienza en AZAR | Por medir | Por medir | 0 | Por medir |
| Inicial / 1 | Alfa-Beta | No aplica: comienza en AZAR | Por medir | Por medir | Por medir | Por medir |
| Inicial / 2 | Minimax | No aplica: comienza en AZAR | Por medir | Por medir | 0 | Por medir |
| Inicial / 2 | Alfa-Beta | No aplica: comienza en AZAR | Por medir | Por medir | Por medir | Por medir |
| Estado de decisión documentado | Ambos, en filas separadas | Por medir | Por medir | Por medir | Por medir | Por medir |

Definan los parámetros:

- **Calidad de la decisión:** acción y utilidad esperada; verifican que coincidan dentro de una tolerancia numérica.
- **Esfuerzo:** `Contador.nodos` cuenta visitas, no estados únicos.
- **Poda:** `Contador.podas` cuenta cortes; no equivale a nodos ahorrados.
- **Tiempo:** duración del cálculo, separada de animaciones y pausas de pantalla.
- **Nodos evitados:** `100 × (1 − nodos_AlfaBeta / nodos_Minimax)`.
- **Ahorro de tiempo:** `100 × (1 − tiempo_AlfaBeta / tiempo_Minimax)`; puede resultar negativo.
- **Profundidad y memoria:** el prototipo no las mide. Si son requisitos, agreguen instrumentación antes de publicar cifras. No conviertan tiros en profundidad sin contar también nodos de decisión y azar.
- **Completitud y optimalidad:** expliquen la finitud del árbol y la elección según utilidad esperada; sostengan la equivalencia de la poda con pruebas, no solo con una captura.

Procedimiento sugerido: repetir cada medición al menos cinco veces en el mismo equipo, conservar el límite de tiros y el orden de sucesores, y reportar mediana de tiempo junto con nodos y valores. Usen la consola para medir sin la comparación concurrente de la interfaz. `comparar.correr` cambia `reglas.maxTiros`; ejecuten estos experimentos en un proceso separado del juego.

Como reseña de rutas, documenten una partida paso a paso: jugador → dados → jugada → acción → tiros restantes → resultado final. Para comparar métodos, acompañen esa ruta con las decisiones de ambos sobre los mismos estados.

### 7. Límites que deben declarar antes de concluir

- El turno actual es por bloques A → B, no alternado entre lanzamientos. B conoce la jugada final de A.
- Obtener 21 no termina inmediatamente toda la partida: el otro jugador puede igualarlo.
- La interfaz obliga a plantarse con 21, mientras el modelo de `sucesores` permite relanzarlo si quedan tiros. Declaren o corrijan esa diferencia antes de afirmar que ambos representan exactamente las mismas acciones.
- Los empates se muestran como final; no hay repetición automática de rondas.
- El árbol no usa caché de estados ni registra memoria o profundidad máxima.
- `comparar.py` informa si los valores coinciden, pero no sustituye una validación amplia de acciones y estados. Si no coinciden, investiguen antes de concluir que la poda conserva el resultado.

Terminen la evaluación con conclusiones respaldadas por sus tablas: coincidencias observadas, reducción de exploración, comportamiento del tiempo y limitaciones del prototipo.
