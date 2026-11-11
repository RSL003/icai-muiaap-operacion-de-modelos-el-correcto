# Solución — microejercicios HTTP y JSON

## 1. Tres formas de pedir una predicción

| Caso | ¿Sale del proceso Python? | ¿Usa HTTP? | ¿La ruta nombra una acción o un recurso? |
| --- | --- | --- | --- |
| A | No | No | No hay ruta HTTP; es una función local. |
| B | Sí, del cliente al servidor | Sí | Acción: `runPumpModel`. |
| C | Sí, del cliente al servidor | Sí | Recurso: `predictions`. |

Para una API nueva elegiría C: el método expresa la operación y la ruta nombra
el recurso.

## 2. URL

- scheme: `http`
- host: `127.0.0.1`
- port: `8000`
- path: `/v1/predictions/pred-42`
- query: `include=explanation` y `limit=1`
- el identificador va en el path; el límite en query; las medidas en un body
  JSON.

## 3. JSON

```json
{"machine_id": "pump-017", "ready": true, "comment": null, "axes": [1, 2]}
```

## 4. Cuatro estados HTTP esenciales

- `200`: la predicción se ha calculado correctamente.
- `400`: no se puede interpretar el texto JSON inválido.
- `422`: el JSON se entiende, pero una medición incumple el contrato.
- `503`: la petición es válida, pero el modelo no está disponible
  temporalmente.

## 5. Crear y consultar una predicción

```text
POST /v1/predictions
GET  /v1/predictions/pred-42
```

Las mediciones van en el body JSON del POST y `pred-42` va en el path del GET.
El POST no es seguro porque solicita una creación. El POST no es idempotente por
defecto porque repetirlo puede crear otra predicción. El GET es seguro porque
solo lee. El GET es idempotente porque repetirlo conserva el mismo efecto
esperado.
