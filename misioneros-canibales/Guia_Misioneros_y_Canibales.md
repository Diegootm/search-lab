# Cómo leer y entender el código de Misioneros y Caníbales

Esta guía explica cómo está organizado el proyecto, qué representa el
problema, cómo funcionan las búsquedas BFS y A\*, cómo se calculan las
métricas y cómo se conecta todo con la interfaz de Pygame.

La mejor forma de estudiarlo es seguir el recorrido de los datos:
primero se define el problema, después los algoritmos lo resuelven,
luego se calculan las métricas y finalmente la interfaz presenta los
resultados.

## 1. Entiende primero el problema

Hay tres misioneros y tres caníbales en la orilla izquierda de un río.
Todos deben llegar a la orilla derecha utilizando un bote que puede
transportar una o dos personas.

Las reglas principales son:

-   El bote no puede cruzar vacío.
-   En cada orilla, si hay misioneros, los caníbales no pueden ser más
    numerosos que ellos.
-   Si en una orilla no hay misioneros, la restricción de comparación no
    se aplica allí.
-   Cada cruce cuesta `1`; por tanto, el costo total de una solución es
    su número de cruces.

El programa no necesita guardar por separado las personas de ambas
orillas. Guarda cuántos misioneros y caníbales quedan a la izquierda;
los de la derecha se calculan por diferencia.

## 2. `problema.py`: la definición formal

Empieza por este archivo, porque los algoritmos dependen de sus reglas.

### Representación del estado

Cada estado tiene la forma `(M, C, B)`:

-   `M`: cantidad de misioneros en la orilla izquierda.
-   `C`: cantidad de caníbales en la orilla izquierda.
-   `B`: posición del bote: `1` significa izquierda y `0` significa
    derecha.

Los estados importantes son:

-   Estado inicial: `(3, 3, 1)`. Todos están a la izquierda y el bote
    también.
-   Estado objetivo: `(0, 0, 0)`. Ya no quedan personas a la izquierda y
    el bote está a la derecha.

La clase `Estado` representa esa tupla y permite consultar cuántos
misioneros y caníbales hay en la orilla derecha.

### Acciones u operadores

`ACCIONES` contiene los cinco tipos de viaje posibles:

  Acción     Personas que viajan
  ---------- -------------------------
  `(1, 0)`   1 misionero
  `(2, 0)`   2 misioneros
  `(0, 1)`   1 caníbal
  `(0, 2)`   2 caníbales
  `(1, 1)`   1 misionero y 1 caníbal

La dirección depende de dónde esté el bote. Si está a la izquierda, las
personas indicadas se restan de esa orilla; si está a la derecha, el
movimiento se interpreta en sentido contrario.

### Validación de los estados

Cuando estudies las funciones que generan sucesores, fíjate en este
orden lógico:

1.  Elegir una acción posible.
2.  Comprobar que las personas que viajan están en la orilla donde se
    encuentra el bote.
3.  Calcular el nuevo estado.
4.  Comprobar que las cantidades están dentro de los límites permitidos.
5.  Comprobar la regla de seguridad en ambas orillas.
6.  Aceptar el estado si cumple las reglas; de lo contrario, rechazarlo
    e indicar el motivo.

Las funciones que enumeran todos los estados y filtran los válidos
permiten explorar el espacio de estados del problema.

### Heurísticas de A\*

El proyecto ofrece dos heurísticas:

-   `h_personas(estado)`: cuenta las personas que siguen en la orilla
    izquierda (`M + C`). Es informativa, pero **no es admisible en
    general**: puede sobreestimar los cruces que faltan.
-   `h_cruces_minimos(estado)`: estima los cruces restantes usando un
    problema relajado. Está diseñada para ser admisible y consistente,
    por lo que es la opción apropiada cuando se quiere que A\* conserve
    la garantía de optimalidad.

No confundas una heurística con el costo real. La heurística estima el
costo que falta; el costo real acumulado se representa por `g`.

## 3. `busqueda.py`: cómo se encuentra la solución

Este archivo contiene la lógica de búsqueda, independiente de la
interfaz gráfica.

### Nodo de búsqueda

Un nodo representa un estado dentro del proceso de búsqueda. Además del
estado, el algoritmo necesita conservar información como:

-   El nodo anterior o padre, para reconstruir la ruta.
-   La acción que llevó al estado.
-   `g`: costo acumulado desde el inicio.
-   `h`: estimación del costo restante, utilizada por A\*.
-   `f`: prioridad calculada como `g + h`, utilizada por A\*.

El resultado de una búsqueda también reúne información sobre si se
encontró la meta, la ruta solución, los nodos generados o expandidos,
los estados visitados y la traza del proceso.

### BFS: búsqueda en anchura

BFS explora primero los estados más cercanos al inicial, por niveles.
Utiliza una cola FIFO: el primero que entra es el primero que sale.

Idea general:

1.  Colocar el estado inicial en la frontera.
2.  Extraer el siguiente nodo de la cola.
3.  Si es el objetivo, reconstruir y devolver la solución.
4.  En caso contrario, generar sus sucesores válidos.
5.  Evitar volver a explorar estados que ya se hayan tratado.
6.  Añadir los estados nuevos al final de la cola y continuar.

Como cada cruce tiene el mismo costo (`1`), BFS encuentra una solución
con el menor número de cruces.

### A\*: búsqueda informada

A\* usa una cola de prioridad. En lugar de procesar los nodos solamente
por orden de llegada, prioriza el menor valor de:

`f(n) = g(n) + h(n)`

-   `g(n)`: cruces realizados para llegar al estado actual.
-   `h(n)`: estimación de los cruces que faltan.
-   `f(n)`: estimación del costo total de la ruta pasando por ese nodo.

A\* puede orientar la exploración hacia estados que parecen más
prometedores. Para mantener la garantía de solución óptima, es
importante utilizar una heurística admisible; en este proyecto, esa
opción es `cruces`.

### ¿Por qué registrar la traza?

La traza guarda información de cada paso de la búsqueda: qué nodo se
seleccionó, qué sucesores se consideraron, cuáles fueron inválidos o
repetidos y cómo quedó la frontera.

Esto permite explicar el comportamiento del algoritmo, no solamente
mostrar la solución final.

## 4. `metricas.py`: medir y explicar el resultado

Este módulo reúne utilidades para medir tiempos, presentar métricas,
convertir la ruta en texto y describir teóricamente los algoritmos.

Conviene distinguir dos tipos de resultados:

-   **Métricas observadas:** valores obtenidos al ejecutar el programa,
    como nodos expandidos, nodos generados, estados visitados y tiempo
    promedio.
-   **Evaluación teórica:** propiedades generales del algoritmo, como
    completitud, optimalidad y complejidad temporal y espacial.

El tiempo de ejecución puede cambiar entre ejecuciones y equipos. Por
eso el programa puede repetir las búsquedas y calcular un promedio. No
concluyas que un algoritmo siempre es más rápido solo por una medición
aislada.

## 5. `comparar.py`: ejecutar BFS y A\* desde la consola

Este archivo coordina los dos algoritmos sobre el mismo problema y
presenta sus resultados.

Comandos útiles:

``` bash
python comparar.py
```

Ejecuta la comparación normal.

``` bash
python comparar.py --traza
```

Además, muestra el proceso de expansión de los nodos.

``` bash
python comparar.py --heuristica personas
```

Ejecuta A\* usando la heurística que cuenta las personas que faltan por
cruzar. Recuerda que esta heurística no es admisible en general.

``` bash
python comparar.py --repeticiones 1000
```

Aumenta el número de repeticiones utilizadas para promediar los tiempos.

Por defecto, A\* utiliza la heurística `cruces`, que es la opción
admisible del proyecto.

## 6. `interfaz.py`: visualizar y probar el problema

La interfaz de Pygame utiliza las reglas y los algoritmos definidos en
los otros módulos. Su objetivo es que se pueda observar la solución,
estudiar la búsqueda, comparar métricas y jugar manualmente.

### Pestañas o modos

-   **Simulación:** selecciona BFS o A\*, resuelve el problema y permite
    recorrer la ruta animada.
-   **Proceso / Árbol:** muestra pasos de la búsqueda, sucesores,
    frontera y valores relevantes.
-   **Comparación:** presenta las métricas obtenidas de BFS y A\*.
-   **Modo manual:** permite que el usuario realice cruces; el programa
    valida los movimientos y puede ofrecer pistas.

### Atajos de teclado

  Tecla              Acción
  ------------------ -----------------------------------
  `Tab`              Cambiar de pestaña
  `Espacio`          Reproducir o pausar
  `←` / `→`          Retroceder o avanzar
  `Inicio` / `Fin`   Ir al inicio o al final
  `B`                Seleccionar BFS
  `A`                Seleccionar A\*
  `H`                Cambiar la heurística
  `R`                Resolver
  `F12`              Guardar una captura
  `1`--`5`           Elegir movimientos en modo manual
  `Retroceso`        Deshacer en modo manual
  `P`                Solicitar una pista
  `Esc`              Salir

La interfaz también incluye una opción para generar capturas de las
vistas, útil para documentación o presentación del proyecto.

## 7. `main.py`: punto de entrada

`main.py` es el archivo de inicio de la aplicación. Su función es llamar
a la función principal de la interfaz.

Por eso, si quieres abrir la versión gráfica, ejecuta:

``` bash
python main.py
```

Si necesitas entender las reglas o los algoritmos, no empieces por aquí:
sigue el flujo hacia `interfaz.py`, `busqueda.py` y `problema.py`.

## 8. `README.md`: resumen del proyecto

El README presenta el enunciado y la metodología general. Recomienda
comparar dos métodos de búsqueda para evaluar completitud, optimalidad y
complejidad temporal y espacial.

El código disponible compara **BFS y A**\*. Por tanto, al explicar el
proyecto, describe esa comparación implementada; no digas que hay una
implementación de DFS si no se ha añadido al código.

## 9. Cómo se conectan todos los archivos

El flujo general es:

1.  `main.py` inicia la aplicación gráfica.
2.  `interfaz.py` presenta las opciones y solicita una búsqueda cuando
    corresponde.
3.  `busqueda.py` ejecuta BFS o A\*.
4.  Los algoritmos consultan `problema.py` para conocer los estados,
    acciones, reglas y heurísticas.
5.  El algoritmo devuelve la ruta, la traza y las métricas de búsqueda.
6.  `metricas.py` ayuda a medir y presentar los resultados.
7.  `interfaz.py` muestra la ruta, el proceso o la comparación;
    alternativamente, `comparar.py` imprime la comparación en la
    consola.

## 10. Orden recomendado para estudiar el código

No intentes comprender las líneas de todos los archivos de una sola vez.
Sigue este orden:

1.  **`README.md`:** entiende el objetivo y las reglas.
2.  **`problema.py`:** identifica el estado, el estado inicial y final,
    las acciones y las validaciones.
3.  **`busqueda.py`:** entiende primero el nodo y luego el
    funcionamiento de BFS; después estudia A\* y sus valores `g`, `h` y
    `f`.
4.  **`comparar.py`:** observa cómo se llaman ambos algoritmos y cómo se
    imprimen sus resultados.
5.  **`metricas.py`:** revisa cómo se miden y presentan las métricas.
6.  **`interfaz.py`:** empieza por la clase `App`, sus modos y las
    funciones que llaman a los algoritmos; después estudia los detalles
    de dibujo y animación.
7.  **`main.py`:** confirma cómo se inicia la aplicación.
