# Tarea 3.2 resuelta: inferencia de vino

Esta es la copia completada del starter. El original permanece intacto.
El modelo entregado está en `models/wine_quality_classifier.joblib`, fuera de
Git. No se ha entrenado ni modificado.

Desde esta carpeta:

```bash
uv sync --frozen
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
uv run python -m model_inference.predict_file --input assets/inference_samples.csv --output resultados/wine_predictions.csv
```

La explicación está en [la nota técnica](../../nota_tecnica.md).
Las cinco predicciones reales están en
[resultados/wine_predictions.csv](resultados/wine_predictions.csv).
