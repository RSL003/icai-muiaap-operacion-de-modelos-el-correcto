"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib

from .preprocess import FEATURE_NAMES, WineFeatures


DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "wine_quality_classifier.joblib"
)


@dataclass(frozen=True, slots=True)
class WineQualityModel:
    estimator: Any
    model_version: str


def load_wine_quality_model(
    model_path: Path = DEFAULT_MODEL_PATH,
) -> WineQualityModel:
    payload = joblib.load(model_path)

    if not isinstance(payload, dict):
        raise ValueError("El artefacto debe ser un diccionario.")

    names = payload.get("feature_names")
    if not isinstance(names, (list, tuple)) or tuple(names) != FEATURE_NAMES:
        raise ValueError("feature_names no coincide con el orden esperado.")

    estimator = payload.get("estimator")
    if not all(
        callable(getattr(estimator, method, None))
        for method in ("predict", "predict_proba")
    ):
        raise ValueError(
            "El artefacto no contiene un clasificador compatible."
        )

    version = payload.get("model_version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("model_version debe ser un texto no vacío.")

    return WineQualityModel(
        estimator=estimator,
        model_version=version,
    )


def infer_wine_quality(
    model: WineQualityModel,
    features: WineFeatures,
) -> tuple[str, float]:
    vector = [features.as_vector()]

    category = model.estimator.predict(vector)[0]
    confidence = max(model.estimator.predict_proba(vector)[0])

    return str(category), round(float(confidence), 2)