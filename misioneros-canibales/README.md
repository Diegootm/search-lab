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

**Metodologías implementadas: BFS (búsqueda en anchura) y A\*.**

---

## Cómo ejecutarlo (paso a paso)

### Requisitos

- **Python 3.12** (la versión que acordó el equipo en el README principal).
  Verifica con `python --version`. En Windows, si `python` no funciona, prueba con `py`.
- **Git**, para clonar el repositorio.
- La única librería necesaria es **Pygame**; se instala en el paso 4.

### Paso 1: clonar el repositorio (solo la primera vez)

```bash
git clone https://github.com/Diegootm/search-lab.git
cd search-lab
```

Si ya lo tienes clonado, entra a la carpeta `search-lab` y actualízalo con `git pull`.

### Paso 2: crear el entorno virtual (solo la primera vez)

Desde la carpeta `search-lab`:

```bash
python -m venv venv
```

### Paso 3: activar el entorno virtual (cada vez que abras una terminal nueva)

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / Mac:**
```bash
source venv/bin/activate
```

Cuando está activo aparece `(venv)` al inicio de la línea.

### Paso 4: instalar las dependencias (solo la primera vez)

```bash
pip install -r misioneros-canibales/requirements.txt
```

### Paso 5: entrar a la carpeta del problema

```bash
cd misioneros-canibales
```

### Paso 6: abrir el prototipo

```bash
python main.py
```

Se abre una ventana de 1280×800. Para ver la solución:

1. En el panel derecho elige **BFS** o **A\***.
2. Pulsa **Resolver** (botón verde).
3. Pulsa **Reproducir** para ver la animación del bote cruzando, o
   **Siguiente / Anterior** para avanzar un cruce a la vez.
4. Usa las pestañas de arriba para ver el **árbol de búsqueda**, la **comparación**
   entre los dos algoritmos o para **jugar en modo manual**.
5. Para cerrar, pulsa `Esc` o cierra la ventana.

### Otros comandos

Todos se ejecutan dentro de `misioneros-canibales/` con el entorno virtual activado:

| Qué hace | Comando |
|----------|---------|
| Abre el prototipo gráfico | `python main.py` |
| Compara BFS vs A\* en la consola (ruta y métricas) | `python comparar.py` |
| Igual, mostrando cada nodo expandido y la frontera | `python comparar.py --traza` |
| Usa en A\* la heurística M + C sugerida arriba | `python comparar.py --heuristica personas` |
| Promedia el tiempo con más ejecuciones (por defecto 200) | `python comparar.py --repeticiones 1000` |
| Guarda los resultados en un archivo de texto | `python comparar.py --traza > resultados.txt` |
| Genera automáticamente las 12 capturas en `capturas/` | `python main.py --capturas` |
| Ejecuta las pruebas automáticas | `python -m unittest discover -s tests -v` |

### Generar el ejecutable (.exe)

Con el entorno virtual activado y dentro de `misioneros-canibales/`:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MisionerosCanibales main.py
```

El ejecutable queda en `dist/MisionerosCanibales.exe`. Cópialo a esta carpeta, como
indica el README principal. Las capturas que se tomen con `F12` desde el ejecutable se
guardan en una carpeta `capturas/` junto al `.exe`.

### Problemas comunes

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'pygame'` | No está activado el entorno virtual (paso 3) o falta instalar las dependencias (paso 4). |
| `python` no se reconoce (Windows) | Usa `py` en lugar de `python`, o reinstala Python marcando *Add Python to PATH*. |
| `No such file or directory: main.py` | No estás dentro de `misioneros-canibales/` (paso 5). También funciona desde la raíz con `python misioneros-canibales/main.py`. |
| La ventana no entra en la pantalla | Se necesita una resolución de al menos 1280×800. |

### Detalle de las pestañas y atajos de teclado

La ventana (1280×800) tiene cuatro pestañas:

1. **Simulación**: se elige la metodología (**BFS** o **A\***) y se pulsa
   **Resolver**. Luego se recorre la ruta solución con *Siguiente / Anterior /
   Reproducir* y se ve el bote cruzando el río con los pasajeros. Muestra el estado
   actual `(M, C, B)`, el movimiento, la ruta solución completa (se puede hacer clic
   en una fila para ir a ese paso), el proceso de búsqueda (cada nodo expandido con
   sus sucesores nuevos, repetidos o inválidos y la frontera) y las métricas.
2. **Proceso / Árbol**: dibuja el árbol de búsqueda expansión por expansión,
   resaltando el nodo que se está expandiendo, la frontera, los expandidos y la ruta
   final. En A\* cada nodo muestra `g + h = f`. A la derecha se detallan los 5
   operadores aplicados al nodo (con el motivo de los inválidos) y la frontera ordenada.
3. **Comparación**: tabla de métricas reales de ambas búsquedas, gráfico de barras,
   parámetros de evaluación (completitud, optimalidad, complejidad) y conclusiones.
4. **Modo manual**: el usuario juega moviendo el bote. Se rechazan los movimientos
   inválidos indicando el motivo, se avisa cuando se vuelve a un estado ya visitado
   (ciclo) y el botón **Pista (BFS)** sugiere el siguiente movimiento óptimo.

Atajos: `Tab` cambia de pestaña · `Espacio` reproduce/pausa · `←` `→` paso a paso ·
`Inicio`/`Fin` · `B` = BFS · `A` = A\* · `H` = cambia la heurística · `R` = resolver ·
`1`–`5` = movimientos en modo manual · `Retroceso` = deshacer · `P` = pista ·
`F12` = captura de pantalla (se guarda en `capturas/`) · `Esc` = salir.

---

## Formulación del problema

| Elemento | Definición |
|----------|------------|
| **Estado** | `(M, C, B)`: `M` misioneros y `C` caníbales en la **orilla izquierda**; `B = 1` si el bote está en la izquierda, `0` si está en la derecha. La orilla derecha es `(3 − M, 3 − C)`. |
| **Estado inicial** | `(3, 3, 1)`: todos y el bote en la orilla izquierda |
| **Estado objetivo** | `(0, 0, 0)`: todos y el bote en la orilla derecha |
| **Operadores** | Mover en el bote `(m, c)` ∈ { `1M`, `2M`, `1C`, `2C`, `1M 1C` } (1 o 2 personas). Si `B = 1` se restan de la izquierda; si `B = 0` se suman. El bote siempre cambia de orilla. |
| **Restricciones** | `0 ≤ M, C ≤ 3` y, en cada orilla, `misioneros = 0` o `misioneros ≥ caníbales`. |
| **Test objetivo** | `estado == (0, 0, 0)` |
| **Costo** | 1 por cruce, así que el costo de la ruta es el número de cruces. |
| **Conjunto de estados** | 4 · 4 · 2 = **32** estados posibles, de los cuales **20 son válidos**; 15 son alcanzables desde el inicial. |

### REAS y tabla percepción → acción (base para el informe)

| REAS | Agente resolvedor |
|------|-------------------|
| **R**endimiento | Llevar a las 6 personas a la otra orilla, sin estados inválidos y con el menor número de cruces |
| **E**ntorno | Río con dos orillas, 3 misioneros, 3 caníbales y un bote para 1 o 2 personas (totalmente observable, determinista, discreto, estático) |
| **A**ctuadores | Mover el bote con 1M, 2M, 1C, 2C o 1M 1C |
| **S**ensores | Lectura del estado `(M, C, B)`: personas en cada orilla y posición del bote |

| Percepción `(M, C, B)` | Acción (ruta óptima) |
|------------------------|----------------------|
| (3, 3, 1) | 2C → |
| (3, 1, 0) | ← 1C |
| (3, 2, 1) | 2C → |
| (3, 0, 0) | ← 1C |
| (3, 1, 1) | 2M → |
| (1, 1, 0) | ← 1M 1C |
| (2, 2, 1) | 2M → |
| (0, 2, 0) | ← 1C |
| (0, 3, 1) | 2C → |
| (0, 1, 0) | ← 1M |
| (1, 1, 1) | 1M 1C → |
| (0, 0, 0) | objetivo: no hacer nada |

**Función sucesor**: aplica los 5 operadores y descarta los que dejan cantidades
fuera de rango o una orilla en peligro. Por ejemplo, desde `(3, 3, 1)`:

| Operador | Resultado | ¿Válido? |
|----------|-----------|----------|
| 1M | (2, 3, 0) | No: orilla izquierda 3C > 2M |
| 2M | (1, 3, 0) | No: orilla izquierda 3C > 1M |
| 1C | (3, 2, 0) | Sí |
| 2C | (3, 1, 0) | Sí |
| 1M 1C | (2, 2, 0) | Sí |

### Algoritmos

Ambos son **búsquedas en grafo** sobre la misma formulación (`problema.py`): guardan
los estados ya alcanzados para no generar estados repetidos ni ciclos, y cada nodo
guarda su **padre**, que se usa para reconstruir la ruta solución.

- **BFS (búsqueda en anchura)**: frontera FIFO. El test objetivo se aplica al
  *generar* el nodo. Es completa y, como todos los cruces cuestan 1, óptima.
- **A\***: frontera ordenada por `f(n) = g(n) + h(n)` (empates: menor `h`, luego orden
  de llegada). El test objetivo se aplica al *extraer* el nodo de la frontera.
  - Heurística por defecto (`cruces`): parte de la sugerencia del README (*personas
    que faltan por cruzar*, `n = M + C`) y la convierte en el **número mínimo de
    cruces del problema relajado** (ignorando la restricción de los caníbales):
    `2n − 3` si el bote está a la izquierda (`1` si `n ≤ 2`), `2n` si está a la
    derecha y `0` en el objetivo. Es **admisible y consistente**, así que A\*
    garantiza la solución óptima.
  - Heurística alternativa (`personas`): `h = M + C`, tal como la sugiere el README.
    **No es admisible** (en `(1, 1, 1)` vale 2 y basta un cruce), por eso se deja
    solo como opción para comparar (tecla `H` o `--heuristica personas`).

---

## Resultados (ejecución real, `python comparar.py`)

Ambas metodologías encuentran la **misma ruta óptima de 11 cruces**:

```
 0. (3, 3, 1)  Estado inicial
 1. (3, 1, 0)  Cruzan 2 caníbales (izq → der)
 2. (3, 2, 1)  Cruza 1 caníbal (der → izq)
 3. (3, 0, 0)  Cruzan 2 caníbales (izq → der)
 4. (3, 1, 1)  Cruza 1 caníbal (der → izq)
 5. (1, 1, 0)  Cruzan 2 misioneros (izq → der)
 6. (2, 2, 1)  Cruzan 1 misionero y 1 caníbal (der → izq)
 7. (0, 2, 0)  Cruzan 2 misioneros (izq → der)
 8. (0, 3, 1)  Cruza 1 caníbal (der → izq)
 9. (0, 1, 0)  Cruzan 2 caníbales (izq → der)
10. (1, 1, 1)  Cruza 1 misionero (der → izq)
11. (0, 0, 0)  Cruzan 1 misionero y 1 caníbal (izq → der)
```

| Métrica | BFS | A\* (h = cruces) |
|---------|----:|-----------------:|
| Longitud de la solución (cruces) | 11 | 11 |
| Costo de la ruta | 11 | 11 |
| Nodos generados | 29 | 28 |
| Nodos expandidos | 13 | 12 |
| Estados visitados (distintos) | 15 | 15 |
| Sucesores repetidos descartados | 14 | 13 |
| Sucesores inválidos descartados | 37 | 33 |
| Tamaño máximo de la frontera | 3 | 3 |
| Factor de ramificación efectivo | 2.15 | 2.25 |
| Tiempo promedio (ms, 500 ejecuciones)* | ≈ 0.17 | ≈ 0.22 |

\* El tiempo depende de la computadora; los conteos de nodos son siempre los mismos.

Definición de las métricas:

- **Nodos generados**: nodos creados con un estado válido (incluye la raíz y los
  que luego se descartan por repetidos).
- **Nodos expandidos**: nodos a los que se aplicó la función sucesor.
- **Estados visitados**: estados distintos que llegaron a alcanzarse.
- **Repetidos / inválidos descartados**: sucesores descartados por ser un estado ya
  alcanzado o por violar las restricciones.

| Parámetro | BFS | A\* |
|-----------|-----|-----|
| Completitud | Sí (b finito) | Sí |
| Optimalidad | Sí (costos de paso iguales) | Sí (h admisible y consistente) |
| Complejidad temporal | O(b^d) | O(b^d) en el peor caso, menor con buena h |
| Complejidad espacial | O(b^d) | O(b^d) (guarda todos los nodos) |

**Análisis**: A\* expande un nodo menos que BFS (12 vs 13): no necesita expandir
`(3, 2, 0)`, cuyo `f = 11` es peor que el de la ruta que va siguiendo. La diferencia es
pequeña porque el espacio de estados es muy chico y muy restringido (la solución es
casi un camino único). En tiempo BFS resulta algo más rápido porque A\* paga el
costo de la cola de prioridad y de calcular `h(n)` en cada nodo.

---

## Estructura

```
misioneros-canibales/
├── README.md
├── requirements.txt
├── main.py           # punto de entrada (interfaz gráfica)
├── problema.py       # formulación: estado, operadores, restricciones, heurísticas
├── busqueda.py       # algoritmos BFS y A*, nodos, traza y métricas por ejecución
├── metricas.py       # tablas de métricas, medición de tiempo, evaluación teórica
├── comparar.py       # comparación BFS vs A* por consola
├── interfaz.py       # prototipo Pygame (simulación, árbol, comparación, manual)
├── capturas/         # capturas generadas con `python main.py --capturas`
└── tests/            # pruebas unitarias (problema, búsquedas e interfaz)
```

## Pruebas

```bash
python -m unittest discover -s tests -v
```

Cubren movimientos válidos e inválidos, las restricciones de cada orilla, la
función sucesor, la consistencia de la heurística, estados repetidos y ciclos, la
reconstrucción de la ruta por padres, la optimalidad desde los 20 estados válidos
(comparada con distancias exactas), la coherencia de las métricas y la interfaz
gráfica manejada con eventos de teclado y ratón (sin ventana, con
`SDL_VIDEODRIVER=dummy`).
