# Search Lab — Proyecto de Inteligencia Artificial

Colección de solucionadores de problemas clásicos de IA mediante algoritmos de
búsqueda. Proyecto del primer parcial de la materia Inteligencia Artificial,
Universidad Mayor de San Simón (UMSS).

## Problemas implementados

| Problema | Carpeta | Rama | Equipo |
|----------|---------|------|--------|
| Misioneros y caníbales | `misioneros-canibales/` | `feature/misioneros-canibales` | 3 personas |
| Juego del 21 | `juego-21/` | `feature/juego-21` | 2 personas |

Cada carpeta contiene su propio README con la descripción del problema, la
metodología de resolución y las instrucciones para ejecutarlo.

## Tecnologías

- **Lenguaje:** Python 3.12 (todos deben usar la misma versión)
- **Interfaces gráficas:** Pygame (misioneros) y Tkinter (juego del 21)
- **Ejecutables:** PyInstaller

## Estructura del repositorio

```
search-lab/
├── misioneros-canibales/
│   ├── README.md
│   └── (código + ejecutable)
├── juego-21/
│   ├── README.md
│   └── (código + ejecutable)
└── README.md
```

---

## Guía de inicio (léela antes de programar)

### 1. Verificar la versión de Python

Todos deben tener **Python 3.12**. Verifica con:

```bash
python --version
```

Si no aparece 3.12, descárgala desde https://www.python.org/downloads/

### 2. Clonar el repositorio

```bash
git clone https://github.com/Diegootm/search-lab.git
cd search-lab
```

### 3. Crear y activar el entorno virtual

El entorno virtual aísla las librerías del proyecto para que no choquen con
otras de tu computadora.

**Crear el entorno (una sola vez):**

```bash
python -m venv venv
```

**Activar el entorno (cada vez que vayas a trabajar):**

En Windows:
```bash
venv\Scripts\activate
```

En Linux / Mac:
```bash
source venv/bin/activate
```

Cuando esté activo, verás `(venv)` al inicio de la línea de comandos.

**Desactivar cuando termines:**
```bash
deactivate
```

### 4. Instalar las librerías

Con el entorno activado:

```bash
pip install pygame
pip install pyinstaller
```

(Tkinter ya viene incluido con Python, no se instala.)

---

## Guía de ramas (Git)

El proyecto usa estas ramas:

| Rama | Para qué sirve |
|------|----------------|
| `main` | Rama principal. Solo versiones finales y estables. |
| `dev` | Integración. Aquí se junta el trabajo de ambos equipos antes de pasar a `main`. |
| `feature/misioneros-canibales` | Trabajo del equipo de misioneros y caníbales. |
| `feature/juego-21` | Trabajo del equipo del juego del 21. |

### Cómo moverte a tu rama

**Ver todas las ramas disponibles:**
```bash
git branch -a
```

**Cambiar a la rama que te toca:**
```bash
git checkout feature/misioneros-canibales
```
o
```bash
git checkout feature/juego-21
```

### Flujo de trabajo diario

```bash
# 1. Activa tu entorno virtual
venv\Scripts\activate

# 2. Muévete a tu rama
git checkout feature/juego-21

# 3. Trae los últimos cambios
git pull

# 4. ... programa ...

# 5. Guarda tus cambios
git add .
git commit -m "describe qué hiciste"

# 6. Sube tus cambios a tu rama
git push
```

> **Regla importante:** nadie programa directo en `main`. Cada equipo trabaja en
> su rama `feature/...`, y cuando algo está listo se integra primero a `dev`.

---

## Cómo generar el ejecutable (.exe)

Dentro de la carpeta de tu problema, con el entorno virtual activado:

```bash
pyinstaller --onefile --windowed nombre_del_archivo.py
```

El ejecutable se genera en la carpeta `dist/`. Cópialo a la carpeta de tu problema.

- `--onefile` → genera un solo archivo .exe
- `--windowed` → no abre la consola negra al correr la app

---

## Equipo

**Misioneros y caníbales:**
- [Nombre 1]
- [Nombre 2]
- [Nombre 3]

**Juego del 21:**
- [Nombre 4]
- [Nombre 5]

## Materia

Inteligencia Artificial — Lic. Patricia Rodríguez Bilbao
Ingeniería de Sistemas, UMSS — 2026
