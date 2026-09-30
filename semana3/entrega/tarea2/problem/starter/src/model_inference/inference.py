from pathlib import Path

import joblib

from model_inference.contracts import WineQualityPrediction
from model_inference.preprocess import FEATURE_NAMES

# Partimos de este archivo para que la ruta no dependa del directorio actual.
DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[2] / "models/wine_quality_classifier.joblib"
)


def load_wine_quality_model(model_path=DEFAULT_MODEL_PATH):
    # Solo cargamos el archivo entregado por el profesor, que es de confianza.
    model = joblib.load(model_path)
    if not isinstance(model, dict):
        raise ValueError("El artefacto debe ser un diccionario")

    names = model.get("feature_names")
    if not isinstance(names, (list, tuple)) or list(names) != list(FEATURE_NAMES):
        raise ValueError("feature_names no coincide con el orden de las 11 features")

    version = model.get("model_version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Falta una model_version válida")

    estimator = model.get("estimator")
    if not callable(getattr(estimator, "predict", None)) or not callable(
        getattr(estimator, "predict_proba", None)
    ):
        raise ValueError("El artefacto no contiene un clasificador compatible")

    # classes_ indica a qué categoría corresponde cada probabilidad.
    classes = getattr(estimator, "classes_", None)
    if classes is None or len(classes) == 0:
        raise ValueError("El clasificador no tiene classes_")
    return model


def infer_wine_quality(features, model, sample_id):
    estimator = model["estimator"]
    # El modelo espera una lista de filas, aunque solo enviemos una.
    rows = [features.as_vector()]
    label = str(estimator.predict(rows)[0])
    probabilities = estimator.predict_proba(rows)[0]

    # La confianza es la probabilidad de la categoría que se ha predicho.
    position = list(estimator.classes_).index(label)
    return WineQualityPrediction(
        sample_id=sample_id,
        quality_band=label,
        confidence=float(probabilities[position]),
        model_version=model["model_version"],
        preprocessing_version=features.preprocessing_version,
    )
