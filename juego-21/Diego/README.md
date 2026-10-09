# Juego del 21 - Mesa animada

## Instalar y ejecutar en Windows (PowerShell)

Descomprime esta carpeta y abre una terminal en ella.

```powershell
py -3.12 --version
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m tkinter
python ejecutar_juego.py
```

Si PowerShell bloquea la activación, abre CMD y ejecuta `.venv\Scripts\activate.bat`.

- `python ejecutar_juego.py`: abre una sola interfaz y permite elegir Minimax o Alfa-Beta.
- `python ejecutar_minimax.py`: inicia solo Minimax.
- `python ejecutar_alfa_beta.py`: inicia solo Alfa-Beta.
- `python comparar.py --tiros 3`: compara ambos algoritmos desde el mismo estado inicial.
- `python -m unittest pruebas.py`: pruebas de reglas y coincidencia de decisiones.

### Configuración

Cambia `configuracion.py` antes de iniciar la aplicación:

```python
MAX_TIROS = 3
JUGADOR_HUMANO = 0
PAUSA_ENTRE_JUGADAS_MS = 1050
DURACION_LANZAMIENTO_MS = 1650
```

`JUGADOR_HUMANO = 0` significa dos jugadores IA; `1` significa humano contra IA y `2` significa IA contra humano. En modo humano se habilitan los botones **Lanzar dados** y **Plantarse**.

Los tiros máximos también se pueden seleccionar desde la pantalla antes de empezar.

### Reglas implementadas

- J1 juega hasta plantarse, sacar 2 y 1 o alcanzar el número máximo de tiros. Después juega J2.
- Ambos están obligados a efectuar un primer lanzamiento. Volver a tirar sustituye la puntuación obtenida en la tirada anterior.
- Sacar los dados 2 y 1 (en cualquier orden) significa victoria inmediata.
- Si nadie consigue 2 y 1, gana la puntuación mayor.
- Si empatan, comienza otra ronda hasta que exista ganador.
- El modelo de búsqueda evalúa una sola ronda finita. Un empate terminal tiene utilidad 0; el reinicio de rondas forma parte de la interfaz, no del árbol de búsqueda.

## Código separado para el informe

| Archivo | Responsabilidad |
|---|---|
| `motor.py` | Estado, funciones sucesoras, nodo de azar, reglas, terminales y utilidad |
| `minimax.py` | Expectiminimax sin poda; MAX, MIN y esperanza matemática |
| `alfa_beta.py` | Expectiminimax con poda alfa-beta y cotas seguras para nodos de azar |
| `interfaz.py` | Interfaz visual Tkinter, animación del cubilete y dados, transiciones temporizadas, resultados finales |
| `configuracion.py` | Parámetros editables |
| `ejecutar_juego.py` | Punto de entrada de la aplicación con selector de algoritmo |
| `ejecutar_minimax.py` | Punto de entrada directo de Minimax |
| `ejecutar_alfa_beta.py` | Punto de entrada directo de Alfa-Beta |
| `comparar.py` | Comparación por consola desde un estado idéntico |
| `pruebas.py` | Pruebas de reglas y equivalencia de decisiones |

Durante la partida se muestra la mesa, los turnos, las tiradas y la suma. **Solo después de declarar un ganador** se abre una ventana de análisis que muestra las métricas reales de la simulación y una comparación controlada desde el estado inicial.

## Generar un ejecutable de Windows

PyInstaller sigue los `import` del archivo de entrada. **No es necesario unir `interfaz.py`, `motor.py`, `minimax.py` y `alfa_beta.py`**. Todos se incorporan en el paquete compilado.

Desde Windows, crea y activa el entorno virtual indicado al inicio y luego ejecuta:

```powershell
python -m pip install --upgrade pyinstaller
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Juego21IA ejecutar_juego.py
```

Obtendrás `dist\Juego21IA.exe` (una aplicación con selector de algoritmo). También puedes ejecutar `crear_ejecutable_windows.bat` para automatizar el proceso.

Si necesitas entregar **dos ejecutables separados**, usa:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Juego21_Minimax ejecutar_minimax.py
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Juego21_AlfaBeta ejecutar_alfa_beta.py
```

O ejecuta `crear_dos_ejecutables_windows.bat`.

### Una carpeta o un archivo

- `--onefile`: crea **un solo EXE**, aunque tu código fuente conste de varios módulos.
- `--onedir`: crea una carpeta con el EXE y bibliotecas auxiliares. Debes distribuir la carpeta entera. Normalmente inicia más rápido.
- `--windowed`: evita mostrar una consola adicional en Windows.

El resultado de PyInstaller **no necesita Python instalado en la computadora donde se ejecuta**. Compila en Windows para obtener archivos `.exe` de Windows; PyInstaller no compila de forma cruzada desde Linux o macOS.

Si un antivirus hace una comprobación del ejecutable de archivo único al iniciar, prueba primero la opción `--onedir`.

### Linux/macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m tkinter
python ejecutar_juego.py
```

Para crear un paquete para Linux/macOS debes usar PyInstaller dentro de ese mismo sistema.

<!-- ## Nota técnica sobre los algoritmos

Minimax y Alfa-Beta comparten el modelo de `motor.py`. Dado que hay azar por los dados, ambas implementaciones son variantes de **Expectiminimax**. El código de Alfa-Beta añade cotas para podar sin descartar de forma incorrecta resultados aleatorios. La reducción de estados no implica que el tiempo de ejecución siempre sea menor.

La comparación del reporte final evalúa una **misma situación inicial** con los dos métodos, no compara los dos recorridos reales de partidas distintas. Los nodos totales mostrados en el panel izquierdo pertenecen a la partida que se acaba de jugar. -->
