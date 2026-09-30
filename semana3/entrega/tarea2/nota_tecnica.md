# Tarea 3.2: módulo de inferencia

He trabajado en una copia del starter dentro de `problem/starter` para no
cambiar los archivos originales de la rama. El CSV, el `pyproject.toml`, el
`uv.lock` y los dos archivos de tests iniciales se conservan como venían.

## Responsabilidades

- `contracts.py` define los once datos de entrada y los cinco campos de salida.
  Pydantic comprueba tipos, límites y campos extra.
- `preprocess.py` coloca los datos en el orden del entrenamiento. No lee CSV.
- `inference.py` carga el joblib, comprueba su estructura, nombres, versión e
  interfaz del clasificador. Después llama a `predict` y `predict_proba` y
  valida la respuesta. No entrena nada.
- `predict_file.py` lee el CSV, separa el identificador, llama a los otros
  módulos y guarda los resultados. No carga joblib directamente.

## Dos decisiones

1. Uso una lista de predicciones en memoria y abro la salida al terminar.
   Así, si una fila falla, no queda un CSV con solo las primeras predicciones.
   Es suficiente para estas cinco muestras. No protege de un fallo del disco
   durante la escritura; la garantía de la práctica es frente a filas inválidas.
2. Uso `FEATURE_NAMES` para ordenar los valores y comparo esa secuencia con
   el artefacto. No uso el orden que tenga el diccionario leído del CSV.
   Así evito intercambiar columnas sin darme cuenta.

## Qué exige cada test inicial

La suite inicial se ejecutó antes de completar los módulos: fallaron los
11 tests porque faltaban las implementaciones.

| Test | Regla que comprueba |
| --- | --- |
| `test_preprocess_preserves_feature_order` | El vector conserva el orden fijado |
| `test_predict_file_writes_predictions_for_kaggle_rows` | Una entrada válida genera la salida esperada |
| `test_predict_file_writes_all_requested_rows` | Se escriben todas las muestras con las cinco columnas |
| `test_predict_file_rejects_an_unknown_csv_column` | No se aceptan columnas desconocidas |
| `test_predict_file_rejects_a_missing_required_field` | No se aceptan medidas ausentes |
| `test_predict_file_rejects_an_out_of_range_field` | Se comprueban los rangos |
| `test_predict_file_leaves_no_output_when_a_later_row_is_invalid` | Una segunda fila inválida no deja salida parcial |
| `test_predict_file_rejects_an_invalid_prediction_category` | Se valida también la categoría de salida |
| `test_predict_file_rejects_an_incomplete_model_artifact` | El artefacto necesita un estimador |
| `test_predict_file_rejects_an_empty_sample_id` | La muestra necesita identificador |
| `test_predict_file_rejects_an_incompatible_model_artifact` | Los nombres y el orden deben coincidir |

Se conservan únicamente los 11 tests originales, sin modificarlos.
Los tests usan modelos pequeños temporales, tal como permite el enunciado.
El comando final usa el artefacto real entregado por el usuario, sin reentrenarlo.

## Resultado de la comprobación

Verificado el 30 de septiembre de 2026 con Python 3.13.15 y el `uv.lock` original:

- `uv run pytest`: 11 tests correctos.
- `uv run ruff check src tests`: sin errores.
- `uv run ruff format --check src tests`: los 7 archivos cumplen el formato.
- CLI con el modelo real: 5 predicciones guardadas en
  `problem/starter/resultados/wine_predictions.csv`.

El artefacto contiene un `RandomForestClassifier`, versión `wine-quality-rf-v1`,
y el orden de sus once características coincide con el contrato.
La ejecución ha clasificado `red-003` como `acceptable` y las otras cuatro
muestras como `needs_review`. El CSV conserva las probabilidades y versiones.
