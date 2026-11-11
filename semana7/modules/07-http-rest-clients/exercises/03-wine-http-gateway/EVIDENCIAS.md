# Evidencias — gateway Wine Quality

- Las 34 pruebas del starter y las comprobaciones Ruff pasan.
- Sin URL, `build_gateway(None)` seleccionó `DemoGateway` y devolvió `acceptable`.
- Con `http://127.0.0.1:8000`, seleccionó `HttpInferenceGateway` y devolvió
  `needs_review` con request ID remoto `req_cccd09132117`.
- POST válido: HTTP 200, request ID `req_5fa91e92cf71`.
- POST inválido: HTTP 422, request ID `req_e51037d51c78`; el campo
  `features.alcohol` debe ser numérico.

Los identificadores corresponden a esta ejecución. Se comprobaron los modos
mediante sus gateways y la API local, sin abrir la interfaz Streamlit.

El gateway traduce 422 a `InputContractError` y 503 a
`ArtifactUnavailableError`; un timeout produce `InferenceTimeoutError` y un
error de conexión produce `ArtifactUnavailableError`. El controlador sigue
usando el contrato de inferencia, sin depender de HTTP.
