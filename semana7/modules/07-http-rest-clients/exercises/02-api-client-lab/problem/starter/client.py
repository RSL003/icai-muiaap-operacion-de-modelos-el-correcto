"""Cliente HTTP completado para el laboratorio."""

from __future__ import annotations

from typing import Any

import requests


class PredictionClientError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None):
        self.status_code = status_code
        super().__init__(message)


def request_prediction(
    payload: dict[str, Any],
    *,
    base_url: str = "http://127.0.0.1:8000",
    timeout: float = 5.0,
    session: Any | None = None,
) -> dict[str, Any]:
    # TODO 3: selecciona `session` o `requests` y envía POST con `json=`,
    # `Accept` y `timeout`. Comprueba los argumentos con test_client.py.
    http_client = session if session is not None else requests
    try:
        response = http_client.post(
            f"{base_url.rstrip('/')}/v1/predictions",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        # TODO 4: llama a `raise_for_status()` y conserva el status de HTTPError.
        response.raise_for_status()
    # TODO 5: traduce Timeout y ConnectionError a PredictionClientError.
    except requests.Timeout as exc:
        raise PredictionClientError("La API tardó demasiado.") from exc
    except requests.ConnectionError as exc:
        raise PredictionClientError("No se pudo conectar con la API.") from exc
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else None
        raise PredictionClientError(
            f"La API respondió con HTTP {status_code}.", status_code=status_code
        ) from exc
    except requests.RequestException as exc:
        raise PredictionClientError(f"Fallo del cliente HTTP: {exc}") from exc

    # TODO 6: convierte la respuesta con `.json()` y exige un diccionario.
    try:
        result = response.json()
    except ValueError as exc:
        raise PredictionClientError("La respuesta no contiene JSON válido.") from exc
    if not isinstance(result, dict):
        raise PredictionClientError("La respuesta JSON debe ser un objeto.")
    return result


if __name__ == "__main__":
    payload = {
        "machine_id": "pump-017",
        "measurements": {
            "temperature_c": 91.2,
            "vibration_mm_s": 8.4,
            "pressure_bar": 4.7,
            "runtime_hours": 12840,
        },
    }

    try:
        result = request_prediction(payload)
        print("Resultado:", result)
    except PredictionClientError as exc:
        print("Error:", exc)
