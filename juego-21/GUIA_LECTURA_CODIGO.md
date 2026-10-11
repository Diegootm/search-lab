# Cómo leer y entender el código del Juego 21

Esta guía corresponde a la versión Pygame que está directamente en esta carpeta. Conviene comprender las reglas y el estado antes de leer los dibujos.

## 1. `reglas.py`: qué significa jugar

Lee primero `maxTiros`, `RESULTADOS` y `P`. Actualmente cada jugador tiene hasta **dos lanzamientos** y existen 36 parejas ordenadas de dados, cada una con probabilidad 1/36.

Después lee estas funciones, en este orden:

1. `valor(d1, d2)`: convierte los dados en un número comparable. El 2 y 1 vale 1000; los dobles valen de 101 a 106; las otras parejas se codifican colocando primero el dado mayor. Estos valores representan un **ranking**, no una suma de puntos.
2. `nombre(resultado)`: convierte ese valor interno en un texto para la pantalla.
3. `utilidad(sA, sB)`: devuelve +1 si gana A, −1 si gana B y 0 si empatan.
4. `estadoInicial`: inicia el árbol antes del primer lanzamiento de A.
5. `es_terminal(e)` y `tipo(e)`: reconocen el final y distinguen nodos MAX, MIN y AZAR.
6. `sucesores(e)`: construye las jugadas futuras; es la función que conecta las reglas con los algoritmos.

Cada estado de búsqueda es `(fase, sA, sB, r)`: fase actual, jugada de A, jugada de B y lanzamientos restantes del jugador activo. `None` significa que todavía no existe una jugada. A completa sus lanzamientos y después juega B, que conoce la jugada final de A.

## 2. `minimax.py`: cómo se evalúa una decisión

Lee `Contador` y después `minimax(e, c)`.

La función se llama recursivamente hasta llegar a `FIN`. En el final usa la utilidad real. En MAX conserva el mayor valor; en MIN, el menor. En AZAR suma la utilidad de cada resultado multiplicada por 1/36. Por eso el algoritmo implementado es **Expectiminimax**, aunque en la interfaz se llame Minimax.

No predice qué dados van a salir: compara el beneficio esperado de las decisiones posibles. `c.nodos` cuenta llamadas al algoritmo, incluso cuando diferentes caminos llegan a estados equivalentes; no hay memoria de estados evaluados.

## 3. `alfaBeta.py`: cómo se evita explorar algunas ramas

Lee `alfabeta(e, alfa, beta, c)` comparándola con `minimax`.

Los casos terminales y los tipos de nodo son los mismos. En MAX y MIN se actualizan los límites alfa y beta y se corta una rama cuando ya no puede mejorar la elección. En AZAR se calculan límites para el promedio usando las utilidades mínima y máxima, −1 y +1: no basta aplicar la poda de un nodo MAX a un lanzamiento.

`c.podas` cuenta **eventos de corte**, no la cantidad exacta de nodos descartados. La reducción real de nodos se obtiene comparando los contadores de ambos algoritmos desde el mismo estado.

## 4. `ia.py`: cómo se elige la acción que se juega

Lee `mejor_accion(e, metodo)` y después `comparar_desde_inicio()`.

`mejor_accion` pide a `sucesores` las acciones legales, evalúa cada una y devuelve `(acción, utilidad esperada, nodos, podas, segundos)`. A busca el mayor valor y B el menor. Si dos acciones tienen exactamente el mismo valor, se conserva la primera: `plantarse` aparece primero en `sucesores`.

`comparar_desde_inicio` evalúa el árbol desde el comienzo con ambos métodos. Su resultado es una comparación del mismo problema, no el resultado de dos partidas con dados distintos.

## 5. `interfaz.py`: cómo se convierte una decisión en una partida

Empieza por `main()`, al final del archivo. Inicializa Pygame, crea `Juego`, inicia la comparación en un hilo y repite: recibir eventos → actualizar tiempos y fase → dibujar → mostrar el fotograma.

Después sigue este recorrido dentro de `Juego`:

1. `__init__`, `botones`, `manejar` y `accion`: configuración del menú y entrada del usuario.
2. `nueva_partida` y `entrar_espera_lanzar`: preparan el turno y las jugadas.
3. `iniciar_lanzamiento`: selecciona los dados reales al azar y prepara la animación.
4. `actualizar`: avanza la animación y los temporizadores según la fase.
5. `terminar_lanzamiento`: guarda los dados, su ranking y el consumo de un tiro.
6. `despues_de_mostrar`: decide si hay que plantarse, esperar al humano o consultar a la IA.
7. `pensar_ia`: construye el estado de búsqueda y evalúa ambos métodos; se juega la acción del método elegido en el menú.
8. `anunciar_ia`, `plantarse` y `pasar_a_b`: muestran la decisión y cambian al siguiente jugador cuando A termina.
9. `terminar_partida` y `dibujar_fin`: calculan el resultado y presentan las métricas.

Ejemplo: A tira → obtiene 43 → decide relanzar → obtiene doble 4 → se planta → B tira y decide conociendo el doble 4 → se comparan las jugadas finales.

La interfaz usa fases como `MENU`, `LANZANDO` o `PENSANDO`; el árbol usa `LANZA_A`, `DECIDE_A` o `FIN`. Son dos representaciones distintas: una organiza la pantalla y la otra modela las posibilidades futuras.

## 6. `dibujos.py`: cómo se presenta el juego

Lee las constantes de colores, `texto` y `dibujar_dado`; después `superficie_cubilete`, `pose_cubilete` y `superficie_fondo_menu`. Estas funciones dibujan y animan, pero no deciden quién gana.

Los colores con sufijo `_JUEGO` corresponden a la partida. Las constantes originales y `superficie_fondo_menu` mantienen la apariencia del menú. En `interfaz.py`, las funciones `dibujar_*` colocan estos elementos en pantalla.

## 7. `comparar.py`: cómo obtener evidencia para el informe

Lee `correr` y `comparar`. Ejecuta cada algoritmo desde el mismo estado para uno y dos lanzamientos por jugador y muestra utilidad, nodos, eventos de poda y tiempo.

Desde esta carpeta:

```powershell
python reglas.py
python comparar.py
python interfaz.py
```

Usa un Python que tenga Pygame instalado para abrir la aplicación. Las comparaciones por consola no necesitan Pygame.

## Aspectos que deben quedar claros al explicarlo

- La jugada nueva reemplaza a la anterior; no se acumulan puntos.
- Esta versión tiene turnos por bloques: A termina y luego juega B.
- El 21 es la jugada máxima, pero A no gana inmediatamente: B también juega y puede conseguir un 21 y empatar.
- Un empate termina la partida; no se reinicia automáticamente una ronda.
- El árbol permite relanzar un 21 si quedan tiros; la interfaz fuerza plantarse. Conviene indicar esta diferencia entre modelo y pantalla en el informe, o unificarla antes de afirmar equivalencia completa.
- El README original propone BFS y DFS, pero los métodos implementados son Expectiminimax y su variante con poda Alfa-Beta.

El orden recomendado completo es: **reglas → Minimax → Alfa-Beta → IA → interfaz → dibujos → comparación**.
