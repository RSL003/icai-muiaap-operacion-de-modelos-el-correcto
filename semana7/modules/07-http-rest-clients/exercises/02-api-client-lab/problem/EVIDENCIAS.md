# Evidencias — cliente de la API de bombas

Peticiones realizadas contra la API local de ejemplo:

| Método y ruta | Content-Type | Estado | request_id | Resultado |
| --- | --- | --- | --- | --- |
| GET /health | application/json | 200 | `req_b1192b2b077e` | `status: ok`, `model_status: ready` |
| POST /v1/predictions | application/json | 200 | `req_a959f363cbe3` | `maintenance_required` es una predicción, no un error HTTP |
| POST /v1/predictions | application/json | 422 | `req_e4a0095bbcaf` | `measurements.vibration_mm_s` debe ser numérico |

El último caso es 422 porque el JSON se interpreta correctamente, pero no
cumple el contrato de entrada; 400 correspondería a JSON mal formado.
Los identificadores son los de esta ejecución y cambian entre peticiones.

Los cinco tests del cliente pasan. No conviene reintentar un POST ciegamente:
si el servidor procesó la primera petición pero se perdió la respuesta, el
reintento podría crear una segunda predicción.
