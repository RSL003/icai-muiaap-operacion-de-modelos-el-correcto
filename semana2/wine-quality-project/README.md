# Wine Quality — Semana 2

Proyecto de la asignatura Operación de Modelos para organizar el entrenamiento
del caso Wine como un paquete Python reproducible. Parte de los tres archivos
de `semana2/starter`: `WineQT.csv`, `train.py` y `test_train.py`.

El objetivo es que otra persona pueda clonar el repositorio, instalar las
dependencias bloqueadas, ejecutar el entrenamiento y comprobar su comportamiento.

## Requisitos

- Git y `uv` instalados.
- Python compatible con `pyproject.toml` (actualmente Python 3.13 o superior).
  El archivo `.python-version` indica la versión seleccionada para el proyecto.
- Una copia local del fork del repositorio del curso.

## Estructura

```text
semana2/wine-quality-project/
├── .python-version
├── README.md
├── pyproject.toml
├── uv.lock
├── data/
│   └── raw/
│       └── WineQT.csv
├── src/
│   └── wine_quality/
│       ├── __init__.py
│       └── train.py
└── tests/
    └── test_train.py
```

- `data/raw/`: dataset de entrada, conservado sin modificar.
- `src/wine_quality/train.py`: carga de datos, entrenamiento y evaluación.
- `tests/test_train.py`: comprobaciones del dataset y del entrenamiento.
- `pyproject.toml`: configuración del paquete y dependencias declaradas.
- `uv.lock`: versiones resueltas de las dependencias para reproducir el entorno.
- `.venv/`: entorno local generado por `uv`; no se versiona en Git.

Pandas y scikit-learn son dependencias de ejecución. Pytest y Ruff pertenecen
al grupo de desarrollo `dev`.

## Instalación desde un checkout limpio

Clona tu fork y abre una terminal en la raíz del repositorio clonado. Desde allí:

```bash
cd semana2/wine-quality-project
uv sync --locked
```

El comando crea el entorno `.venv` e instala las dependencias, incluidas las de
desarrollo, según `uv.lock`. La opción `--locked` exige que el lockfile esté
actualizado respecto a la configuración del proyecto.

Los siguientes comandos se ejecutan desde `semana2/wine-quality-project`.
No es necesario activar manualmente `.venv` al utilizar `uv run`.

## Entrenamiento como módulo

```bash
uv run --frozen python -m wine_quality.train
```

La opción `--frozen` utiliza el lockfile existente sin actualizarlo. La ejecución
debe leer `data/raw/WineQT.csv` y mostrar el número de filas, variables y clases,
además del F1 macro de validación.

Valores esperados del dataset:

- 1143 filas y 13 columnas originales.
- 11 variables predictoras; se excluyen `Id` y la variable objetivo `quality`.
- 6 clases de calidad: 3, 4, 5, 6, 7 y 8.

El modelo es `ExtraTreesClassifier` con 300 árboles. Se utiliza una división
estratificada, con un 15 % de los datos para validación, y la semilla `42` tanto
en la división como en el estimador. El F1 macro obtenido debe registrarse como
evidencia de la ejecución; no se exige un valor mínimo en esta práctica.

## Comprobaciones

```bash
uv run --frozen pytest
uv run --frozen ruff check .
```

El test comprueba la forma del dataset, las clases, la exclusión de `Id`, las
11 variables predictoras, el rango de la métrica y que dos entrenamientos con
la misma configuración produzcan un F1 macro aproximadamente igual.

La entrega debe incluir las salidas reales de estos tres comandos:

```bash
uv run --frozen python -m wine_quality.train
uv run --frozen pytest
uv run --frozen ruff check .
```

El test llama directamente a las funciones de entrenamiento y recibe la ruta
del dataset. Por eso, que Pytest pase no sustituye la comprobación del comando
modular, que también verifica la ruta utilizada por `main()`.

## Resultados de verificación

Verificación realizada el 6 de octubre de 2026 sobre una copia limpia de los
archivos registrados en Git, con un entorno virtual nuevo y Python 3.13.15 en
macOS. La instalación y las tres comprobaciones terminaron correctamente.

| Comando | Resultado |
| --- | --- |
| `uv sync --locked` | Instalación correcta con las versiones de `uv.lock`. |
| `uv run --frozen python -m wine_quality.train` | 1143 filas, 11 variables, 6 clases y F1 macro de validación de 0.3402. |
| `uv run --frozen pytest` | 1 test aprobado (`1 passed`). |
| `uv run --frozen ruff check .` | Sin errores (`All checks passed!`). |

Salida del entrenamiento:

```text
Filas: 1143
Variables: 11
Clases: 6
F1 macro: 0.3402
```

La ruta del dataset en `main()` se construye desde la ubicación de `train.py`
hasta `data/raw/WineQT.csv`. El F1 macro corresponde a la partición de validación
con semilla `42`; es una evidencia de esta ejecución, no una garantía de
rendimiento sobre datos nuevos.

## Entrega en GitHub

El assignment solicita 2–3 commits en la rama `feature/s2-wine-project` y una
pull request abierta desde la web contra `main` del mismo fork. La revisión debe
contener este proyecto y las evidencias de entrenamiento, Pytest y Ruff.

Antes de subir la rama, revisa los archivos incluidos: deben estar el código,
los datos del ejercicio, los tests, este README, `pyproject.toml` y `uv.lock`;
el entorno `.venv` y las cachés deben permanecer fuera de Git.
