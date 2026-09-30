# Entrega de la semana 3

- Tarea 3.1: [lienzo de contrato](tarea1/lienzo.md).
- Tarea 3.2: [código y proyecto](tarea2/problem/starter/) y
  [nota técnica](tarea2/nota_tecnica.md).

Todo está en esta carpeta nueva. No se modifican los ejercicios originales ni
el código previo de la rama. Se utiliza una copia del starter para mantener
su estructura `problem/starter`.

## Ejecutar

Desde la raíz del repositorio:

```bash
cd semana3/entrega/tarea2/problem/starter
uv sync --frozen
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
uv run python -m model_inference.predict_file --input assets/inference_samples.csv --output resultados/wine_predictions.csv
```

Hace falta Python 3.11 o posterior y `uv`. El archivo `uv.lock` fija las
dependencias del starter original.

El modelo entregado está copiado localmente en
`tarea2/problem/starter/models/wine_quality_classifier.joblib`.
La carpeta `models/` está ignorada por Git: no se sube el binario.
En otro equipo hay que colocar ahí el mismo archivo antes de ejecutar el CLI,
o indicar su ubicación con `--model /ruta/al/modelo.joblib`.

El CSV de cinco predicciones se guarda en
`tarea2/problem/starter/resultados/wine_predictions.csv`.
También se puede usar `--output .tmp/wine_predictions.csv`, como en el enunciado.
Los tests no necesitan el modelo real porque crean artefactos temporales.
