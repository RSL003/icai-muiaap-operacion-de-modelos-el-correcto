# Tarea 3.1: contrato de inferencia

## Qué datos usa cada parte

Los datos históricos tienen las medidas del vino y la etiqueta de calidad.
Sirvieron para entrenar. En esta práctica no los necesitamos ni entrenamos nada.

El artefacto `wine_quality_classifier.joblib` es el modelo ya entrenado.
Contiene `estimator`, `feature_names` y `model_version`. Lo carga el módulo de
inferencia y comprueba los nombres y el orden antes de hacer predicciones.

Los datos nuevos son las cinco filas de `inference_samples.csv`. No tienen
la etiqueta `quality`. `sample_id` identifica la muestra, pero no es una medida
del vino y no entra al modelo.

## Tabla de entrada

Todos los límites son inclusivos y son los de la práctica. Son límites de
aceptación para este módulo, no una descripción de todos los vinos posibles.
Los números llegan como texto del CSV y se convierten a `float` al validarlos.
No se aceptan vacíos, valores ausentes, NaN, infinitos ni columnas extra.

| Campo | Tipo validado | Unidad | Mínimo | Máximo | ¿Ausente? |
| --- | --- | --- | --- | --- | --- |
| fixed_acidity | float | g/dm³, ácido tartárico | 0 | 20 | No |
| volatile_acidity | float | g/dm³, ácido acético | 0 | 2 | No |
| citric_acid | float | g/dm³ | 0 | 2 | No |
| residual_sugar | float | g/dm³ | 0 | 20 | No |
| chlorides | float | g/dm³, cloruro sódico | 0 | 1 | No |
| free_sulfur_dioxide | float | mg/dm³ | 0 | 100 | No |
| total_sulfur_dioxide | float | mg/dm³ | 0 | 300 | No |
| density | float | g/cm³ | 0.98 | 1.01 | No |
| ph | float | sin unidad | 2.5 | 4.5 | No |
| sulphates | float | g/dm³, sulfato potásico | 0 | 3 | No |
| alcohol | float | % en volumen | 5 | 20 | No |

Además, el CSV debe llevar `sample_id`: texto no vacío. Se separa antes de
validar las once medidas y se conserva en la salida.

## Flujo y orden

```text
CSV -> separar sample_id -> solicitud validada -> preprocesado -> vector
                                                                 |
artefacto del profesor -> carga y comprobación -> estimador <------+
                                                   |
                                      predicción validada
                                                   |
                            CSV, cuando todas las filas son válidas
```

El orden obligatorio es:

```text
fixed_acidity, volatile_acidity, citric_acid, residual_sugar, chlorides,
free_sulfur_dioxide, total_sulfur_dioxide, density, ph, sulphates, alcohol
```

No se escalan los valores ni se inventan datos ausentes. El preprocesado solo
ordena las medidas validadas. Su versión es `wine-red-features-v1`.

Para `red-001`, el vector es:

```text
[7.4, 0.7, 0.0, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4]
```

Si intercambio `density` y `alcohol`, el vector sigue teniendo once números,
pero el modelo interpreta 9.4 como densidad y 0.9978 como alcohol. Un estimador
que recibe listas no conoce los nombres y puede aceptar esa fila sin avisar.
Por ejemplo, una regla ilustrativa `alcohol > 10` cambia de resultado para
una muestra con alcohol 11 y densidad 0.998 si se intercambian las posiciones.
Esto demuestra el riesgo, no es una predicción del modelo entregado.

Para evitarlo, `FEATURE_NAMES` se define una sola vez. El preprocesado lo usa
para ordenar y el cargador lo compara con los nombres del artefacto.

## Entradas y fallos

Esta es una entrada válida completa:

```csv
sample_id,fixed_acidity,volatile_acidity,citric_acid,residual_sugar,chlorides,free_sulfur_dioxide,total_sulfur_dioxide,density,ph,sulphates,alcohol
red-001,7.4,0.7,0.0,1.9,0.076,11.0,34.0,0.9978,3.51,0.56,9.4
```

| Caso | Cambio respecto a la fila válida | Resultado y etapa |
| --- | --- | --- |
| Válido | Ninguno | Pasa el contrato y llega al modelo |
| Columna desconocida | Añadir `unexpected_field=1` | Pydantic rechaza el campo antes de preprocesar |
| Fuera de rango | Cambiar `ph` a `99` | Pydantic rechaza el rango antes de preprocesar |
| Tipo imposible | Cambiar `alcohol` a `hola` | Pydantic rechaza la conversión a float |
| Falta una medida | Quitar `alcohol` | Pydantic rechaza el campo obligatorio ausente |
| Sin identificador | Dejar `sample_id` vacío | El CLI lo rechaza antes de preprocesar |
| Modelo incompatible | Invertir `feature_names` en el artefacto | El cargador lo rechaza antes de `predict` |

Si falla una fila, el comando termina con código 2, indica la causa y no escribe
el CSV de predicciones. Si ya existía una salida, conserva la anterior.

## Salida

| Campo | Tipo | Regla |
| --- | --- | --- |
| sample_id | str | Identificador de la entrada, no vacío |
| quality_band | str | `needs_review`, `acceptable` o `excellent` |
| confidence | float | Entre 0 y 1, finito |
| model_version | str | Versión del artefacto, no vacía |
| preprocessing_version | str | `wine-red-features-v1` |

Las categorías mantienen la continuidad con el contrato del starter de S4.
La confianza es la probabilidad que devuelve el estimador para la categoría
predicha. No garantiza que la clasificación sea correcta.

Ejemplo inventado solo para mostrar el formato:

```json
{"sample_id": "red-001", "quality_band": "acceptable", "confidence": 0.8,
 "model_version": "wine-quality-rf-v1", "preprocessing_version": "wine-red-features-v1"}
```

## Tres criterios de aceptación

1. El vector tiene once números, respeta el orden anterior y excluye
   `sample_id`. Se comprueba con `test_preprocess_preserves_feature_order`.
2. Una columna extra, una segunda fila inválida o un modelo con orden distinto
   producen error y no crean una salida parcial. Se comprueba con los tests del CLI.
3. El comando de la tarea 2 procesa las cinco muestras y genera las cinco
   columnas de salida indicadas, con confianza entre 0 y 1 y ambas versiones.

Los comandos exactos están en `../README.md`. La tabla y este lienzo son la
entrega de la clase 1; el código de producción está separado en la tarea 2.

## Plan para la clase 2

- `contracts.py`: comprobar entrada y salida con Pydantic.
- `preprocess.py`: construir el vector ordenado y añadir su versión.
- `inference.py`: cargar el artefacto, comprobarlo y pedir la predicción.
- `predict_file.py`: leer el CSV, coordinar las funciones y escribir al final.

Usaría Pydantic al recibir datos externos porque comprueba tipos y rangos.
Usaría una dataclass para guardar el vector interno ya preparado. Una dataclass
por sí sola no rechaza `ph=99`, aunque tenga anotaciones de tipos.
