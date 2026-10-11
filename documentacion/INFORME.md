# Guía del informe: Misioneros y Caníbales y Juego 21

Documento único para preparar el informe de ambos problemas. Las reglas y la guía de lectura del código están en los README de [Misioneros y Caníbales](../misioneros-canibales/README.md) y [Juego 21](../juego-21/README.md).

El informe debe incluir dos metodologías por problema: **BFS y A\*** para Misioneros y Caníbales, y **Expectiminimax y su variante con poda Alfa-Beta** para el Juego 21. El recorrido recursivo en profundidad de Minimax no constituye una implementación de DFS como tercera metodología comparada.

## I. Introducción

Presentar los dos problemas y el propósito de aplicar búsquedas a situaciones diferentes: encontrar una ruta válida de cruces y tomar decisiones frente a un rival con resultados aleatorios. Indicar que los prototipos se implementaron en Python y Pygame.

## II. Objetivos

**2.1 Objetivo general:** implementar y comparar dos metodologías de búsqueda para cada problema, considerando la calidad de la solución y el esfuerzo computacional.

**2.2 Objetivos específicos:** modelar estados y acciones, implementar los cuatro métodos, visualizar la resolución, verificar las restricciones y comparar métricas desde condiciones equivalentes.

## III. Marco teórico

Explicar cada metodología en un máximo de una plana, con referencias verificables de las fuentes realmente consultadas.

| Metodología | Conceptos que deben explicarse |
|---|---|
| BFS | Cola FIFO, exploración por niveles, control de repetidos y costo unitario de cruces. |
| A* | Prioridad `f = g + h`, heurística admisible y consistente, relación con la optimalidad. |
| Expectiminimax | MAX, MIN, AZAR, terminales y utilidad esperada. |
| Alfa-Beta con azar | Límites alfa y beta; acotación del promedio pendiente usando utilidades entre −1 y +1. |

En Misioneros y Caníbales, distinguir las heurísticas `personas` y `cruces`: la primera no es admisible en general; la segunda es la opción admisible usada por defecto. En el Juego 21, aclarar que el nombre Minimax de la interfaz corresponde a Expectiminimax.

## IV. Ingeniería

### 4.1 Descripción, ampliación y abstracción de los problemas

**4.1.1 Misioneros y Caníbales.** Tres misioneros y tres caníbales deben cruzar un río con un bote para una o dos personas. No puede cruzar vacío. En cada orilla con misioneros, los caníbales no pueden superarlos en cantidad. La animación no forma parte del estado de búsqueda.

**4.1.2 Juego 21.** Cada jugador puede plantarse o relanzar, con hasta dos lanzamientos. A completa su jugada antes de que juegue B; B conoce la jugada final de A. La jugada nueva reemplaza la anterior. El ranking es: 21 (dados 2 y 1), dobles de 66 a 11 y parejas normales ordenadas por dado mayor y menor. Los valores internos representan un ranking, no una suma. El empate finaliza la partida.

### 4.2 Formulación de las metas

**4.2.1 Misioneros y Caníbales.** Alcanzar `(0, 0, 0)` desde `(3, 3, 1)` mediante cruces válidos, minimizando el costo unitario acumulado.

**4.2.2 Juego 21.** Obtener una jugada superior al rival. El agente selecciona acciones por utilidad esperada: A maximiza y B minimiza una utilidad expresada desde A. Una buena decisión según el modelo no garantiza ganar una partida concreta.

### 4.3 Formulación de los problemas de búsqueda

Crear un subpunto para cada problema, incluyendo REAS, percepciones → acciones y conjunto problema.

#### REAS

| Elemento | Misioneros y Caníbales | Juego 21 |
|---|---|---|
| Rendimiento | Alcanzar la meta sin infracciones y minimizar cruces. | Optimizar la utilidad esperada y evaluar el esfuerzo de búsqueda. |
| Entorno | Dos orillas, seis participantes y bote para dos. | Dos jugadores, dos dados, ranking y límite de tiros. |
| Actuadores | Transportar pasajeros permitidos. | Plantarse o relanzar. |
| Sensores | Cantidades en cada orilla y posición del bote. | Fase, jugadas conocidas y tiros restantes. |

Misioneros y Caníbales es determinista; el Juego 21 es estocástico y competitivo. Ambos usan estados y acciones discretos.

#### Percepciones → acciones

- **Misioneros y Caníbales:** `(M, C, B)` → combinación legal de pasajeros y cruce en la dirección del bote.
- **Juego 21:** `(fase, jugada_A, jugada_B, tiros_restantes)` → `plantarse` o `relanzar` si quedan tiros; de lo contrario, `plantarse`. Los valores de los dados son resultados aleatorios, no acciones elegidas por el agente.

#### Conjunto problema

| Componente | Misioneros y Caníbales | Juego 21 |
|---|---|---|
| Estados | `(M, C, B)`, con cantidades de la orilla izquierda. | `(fase, sA, sB, r)`. |
| Inicial | `(3, 3, 1)`. | `("LANZA_A", None, None, maxTiros)`. |
| Acciones | `(1,0)`, `(2,0)`, `(0,1)`, `(0,2)`, `(1,1)`, si son legales. | Plantarse y relanzar. |
| Transiciones | Cruces con validación de pasajeros y seguridad. | Decisiones y 36 resultados de dados con probabilidad 1/36. |
| Final | `(0, 0, 0)`. | Fase `FIN` después de completar ambos jugadores. |
| Evaluación | Costo de 1 por cruce. | +1 si gana A, −1 si gana B y 0 si empatan. |

En el Juego 21 no se minimiza un costo de camino: el límite de tiros hace finita la búsqueda y la utilidad define la conveniencia de las decisiones.

### 4.4 Tecnologías y herramientas utilizadas

Documentar Python, Pygame y PyInstaller; añadir las librerías estándar usadas, como `itertools`, `random`, `math`, `threading`, `time`, `collections`, `heapq` y `statistics`, según el módulo que se explique. Registrar las versiones y las características del equipo de medición. No inventar dependencias ni incluir herramientas que no se utilizaron.

Para describir los archivos, usar las tablas de organización de los README técnicos en lugar de mantener listas repetidas en varios documentos.

### 4.5 Implementación de los prototipos y resultados de resolución

**4.5.1 Prototipo de Misioneros y Caníbales.** Describir la simulación, la visualización del proceso de búsqueda, la comparación y el modo manual. Explicar cómo BFS y A* reciben el mismo modelo y devuelven ruta, traza y métricas.

Capturas sugeridas:

1. Estado inicial y selección del algoritmo.
2. Ejecución o ruta obtenida con BFS.
3. Ejecución o ruta obtenida con A* y heurística identificada.
4. Estado meta y vista del proceso de búsqueda.

**4.5.2 Prototipo del Juego 21.** Describir la selección humano/IA, el método elegido, las animaciones, el registro de decisiones y el resultado final. La interfaz calcula ambos métodos sobre cada decisión de IA, pero juega la acción del método seleccionado.

Capturas sugeridas:

1. Menú con modo y algoritmo visibles.
2. Decisión registrada durante una partida con Minimax.
3. Decisión registrada durante una partida con Alfa-Beta.
4. Resultado final con las tablas completas; esperar a que termine el cálculo inicial.

Cada imagen debe tener número, un pie que describa lo que realmente se ve y «Fuente: elaboración propia». Agregar una reseña del estado observado y del resultado. Una captura de otra partida sirve para ilustrar el prototipo, pero no para comparar decisiones desde estados equivalentes.

### 4.6 Evaluación comparativa de las metodologías de búsqueda

Separar condiciones de ejecución, rutas o acciones, métricas y análisis dentro de los dos subpuntos siguientes. No mezclar los cuatro algoritmos en una sola tabla de rendimiento: resuelven objetivos diferentes.

#### 4.6.1 Evaluación de Misioneros y Caníbales

Usar el mismo estado inicial, reglas, orden de acciones y equipo. Para A*, indicar la heurística. Ejecutar desde la raíz:

```powershell
python misioneros-canibales/comparar.py --repeticiones 200
python misioneros-canibales/comparar.py --traza
```

| Método | Solución encontrada | Cruces / costo | Nodos generados | Nodos expandidos | Máxima frontera | Tiempo promedio (ms) |
|---|---|---|---|---|---|---|
| BFS | Por medir | Por medir | Por medir | Por medir | Por medir | Por medir |
| A* (`cruces`) | Por medir | Por medir | Por medir | Por medir | Por medir | Por medir |

Registrar las rutas completas como secuencias de estados y cruces. Verificar la seguridad de cada estado y comparar sus costos. El tamaño máximo de frontera es una medida del almacenamiento de búsqueda, no memoria en bytes. La salida también incluye visitados, descartes y factor de ramificación; definir cada indicador si se incorpora.

Relacionar la evidencia con completitud y optimalidad: BFS es apropiado para costos unitarios; para A* utilizar la heurística admisible y consistente si se quiere justificar la garantía correspondiente. No concluir que A* siempre es más rápido a partir de una ejecución.

#### 4.6.2 Evaluación del Juego 21

Ejecutar desde la raíz:

```powershell
python juego-21/comparar.py
```

| Tiros por jugador | Método | Utilidad esperada | Nodos visitados | Eventos de poda | Tiempo (s) |
|---|---|---|---|---|---|
| 1 | Minimax | Por medir | Por medir | 0 | Por medir |
| 1 | Alfa-Beta | Por medir | Por medir | Por medir | Por medir |
| 2 | Minimax | Por medir | Por medir | 0 | Por medir |
| 2 | Alfa-Beta | Por medir | Por medir | Por medir | Por medir |

Transcribir cifras de ejecuciones completas, sin reconstruir tiempos a partir de porcentajes redondeados. Los valores desde el inicio corresponden a un nodo AZAR, no a una acción concreta.

Para las rutas observadas, registrar jugador → dados → jugada → acción → tiros restantes → resultado. Para comparar decisiones, usar los dos registros calculados sobre el mismo estado; no comparar victorias de partidas con dados diferentes.

Definir los indicadores:

- **Utilidad esperada:** evaluación desde A; positiva favorece a A y negativa a B. No es el resultado final de una partida.
- **Nodos visitados:** llamadas de evaluación; no estados únicos, ya que no hay caché.
- **Eventos de poda:** cortes realizados, no cantidad de nodos eliminados.
- **Tiempo:** cálculo del algoritmo, excluyendo animación y pausas.
- **Nodos evitados (%):** `100 × (1 − nodos_AB / nodos_MM)`.
- **Ahorro de tiempo (%):** `100 × (1 − tiempo_AB / tiempo_MM)`; puede ser negativo.

Se recomienda repetir las mediciones al menos cinco veces y registrar la mediana. Medir por consola evita mezclar el cálculo con la comparación concurrente de la interfaz. `comparar.correr` modifica `reglas.maxTiros`, por lo que debe ejecutarse en un proceso separado del juego.

La coincidencia de valores desde el inicio no prueba por sí sola coincidencia de acciones en todos los estados. La profundidad y la memoria no están instrumentadas; no publicar cifras de esos parámetros sin medirlos.

#### Limitaciones que deben declararse

- Misioneros y Caníbales modela tres participantes de cada tipo y un bote para dos. La heurística `personas` no garantiza optimalidad.
- En el Juego 21 los turnos son por bloques A → B, no alternados entre lanzamientos.
- Obtener 21 no termina inmediatamente toda la partida: B puede igualar a A.
- La interfaz obliga a plantarse con 21, pero el modelo permite relanzarlo si quedan tiros. Declarar esta diferencia antes de afirmar que ambos modelos tienen exactamente las mismas acciones.
- Un empate termina la partida; no comienza automáticamente otra ronda.
- Nodos generados, nodos expandidos, visitas y eventos de poda son indicadores distintos. Comparar métricas equivalentes dentro de cada problema.

## V. Conclusiones

Dedicar un subpunto a cada problema. Relacionar los resultados con los objetivos y responder si las soluciones fueron válidas, si los métodos coincidieron en calidad y qué diferencias se observaron en el esfuerzo de búsqueda. Evitar afirmar superioridad general sin evidencia suficiente.

## VI. Bibliografía

Incluir únicamente fuentes consultadas. Para libros, registrar autor, título, edición, año y páginas. Para documentación técnica, registrar el recurso utilizado. Una referencia posible para el marco teórico es *Artificial Intelligence: A Modern Approach*, de Russell y Norvig, indicando la edición realmente consultada.

## Anexo A. Código fuente y entrega digital

Adjuntar el código de ambos problemas, los ejecutables de `ejecutables/` y el README general con instrucciones. Los binarios existentes se trasladaron sin alterarlos; regenerarlos mediante `scripts/generar_ejecutables.ps1` cuando se cambie el comportamiento de los prototipos.

Organizar las evidencias de esta forma cuando se incorporen al repositorio:

```text
documentacion/
├── INFORME.md
├── capturas/
│   ├── juego-21/
│   └── misioneros-canibales/
└── resultados/
    ├── juego-21.csv
    └── misioneros-canibales.csv
```

Las carpetas de evidencias se crean al guardar capturas y mediciones; no contienen resultados inventados. Excluir entornos virtuales, cachés y temporales de compilación de la entrega final.
