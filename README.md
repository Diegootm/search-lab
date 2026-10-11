# Search Lab — Proyecto de Inteligencia Artificial

Proyecto del primer parcial de Inteligencia Artificial, Ingeniería de Sistemas, Universidad Mayor de San Simón. Integra dos problemas y compara dos metodologías por problema. La rama `dev` reúne el código de ambos prototipos.

| Problema | Metodologías | Documentación técnica |
|---|---|---|
| Misioneros y Caníbales | BFS y A* | [Reglas, ejecución y guía de lectura](misioneros-canibales/README.md) |
| Juego 21 | Expectiminimax y su variante con poda Alfa-Beta | [Reglas, ejecución y guía de lectura](juego-21/README.md) |

Ambas interfaces utilizan **Pygame**.

## Estructura del repositorio

```text
search-lab/
├── juego-21/                Código y documentación técnica
├── misioneros-canibales/    Código, pruebas y documentación técnica
├── ejecutables/            Aplicaciones de Windows listas para usar
│   ├── Juego21.exe
│   └── Misioneros-Canibales.exe
├── documentacion/
│   └── INFORME.md           Guía única del informe de ambos problemas
├── scripts/
│   └── generar_ejecutables.ps1
├── requirements.txt        Dependencias compartidas de ejecución
└── README.md               Inicio y organización del proyecto
```

Las guías de lectura están integradas en los README de cada problema. La planificación del informe está únicamente en [documentacion/INFORME.md](documentacion/INFORME.md).

## Ejecutar en Windows sin instalar Python

Abrir con doble clic [Juego21.exe](ejecutables/Juego21.exe) o [Misioneros-Canibales.exe](ejecutables/Misioneros-Canibales.exe).

Los ejecutables incluyen su entorno de ejecución. Los binarios existentes se trasladaron sin alterarlos; después de modificar la lógica o la interfaz, hay que regenerarlos para distribuir esos cambios.

## Ejecutar desde el código fuente

Usar Python 3.12. Desde la raíz, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe juego-21/interfaz.py
.\.venv\Scripts\python.exe misioneros-canibales/main.py
```

Se llama directamente al Python del entorno para evitar depender de su activación. Los demás comandos requieren ese Python o uno con las dependencias instaladas.

## Comparar los algoritmos

```powershell
python juego-21/comparar.py
python misioneros-canibales/comparar.py --repeticiones 200
```

Las comparaciones se ejecutan por separado: cada módulo `comparar.py` corresponde a un problema diferente.

## Generar los ejecutables de Windows

Instalar PyInstaller en el mismo entorno y ejecutar el script desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\scripts\generar_ejecutables.ps1 -Python .\.venv\Scripts\python.exe
```

El script compila cada aplicación sin consola en un único `.exe`, coloca los resultados en `ejecutables/` y mantiene temporales y especificaciones generadas en `build/`. Debe ejecutarse en Windows.

## Preparar la entrega del informe

1. Seguir [la guía del informe](documentacion/INFORME.md), que cubre ambos problemas.
2. Guardar capturas y tablas en `documentacion/`, organizadas por problema.
3. Adjuntar el código de ambas carpetas y los binarios de `ejecutables/`.
4. Excluir entornos virtuales, `__pycache__/`, `build/` y `dist/` de la entrega; son archivos locales o generados.

Las pruebas, reglas y comandos específicos están en el README de cada problema.
