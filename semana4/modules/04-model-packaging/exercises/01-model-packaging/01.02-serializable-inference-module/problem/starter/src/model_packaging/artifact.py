"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

import math
import os
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

import joblib
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)
from model_packaging.preprocess import FEATURE_NAMES, PREPROCESSING_VERSION
from model_packaging.preprocess import preprocess_wine_request

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
)


class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


class ArtifactManifest(BaseModel):
    """Metadatos legibles y estrictos que acompañan al modelo."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    model_version: str = Field(min_length=1, max_length=80)
    preprocessing_version: str
    feature_names: tuple[str, ...]
    output_labels: tuple[QualityBand, ...]
    estimator_type: str = Field(min_length=1, max_length=120)

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        """Rechaza versiones de manifiesto no compatibles."""

        if value != ARTIFACT_SCHEMA_VERSION:
            raise ValueError(
                f"schema_version incompatible: se esperaba {ARTIFACT_SCHEMA_VERSION}"
            )
        return value

    @field_validator("preprocessing_version")
    @classmethod
    def validate_preprocessing_version(cls, value: str) -> str:
        """Exige el mismo preprocesado que consume la inferencia."""

        if value != PREPROCESSING_VERSION:
            raise ValueError(
                "preprocessing_version incompatible: "
                f"se esperaba {PREPROCESSING_VERSION}"
            )
        return value

    @field_validator("feature_names")
    @classmethod
    def validate_feature_names(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Protege los nombres y el orden de las características."""

        if value != FEATURE_NAMES:
            raise ValueError("feature_names no coincide con el orden del contrato.")
        return value

    @field_validator("output_labels")
    @classmethod
    def validate_output_labels(
        cls, value: tuple[QualityBand, ...]
    ) -> tuple[QualityBand, ...]:
        """Limita las etiquetas declaradas a las categorías admitidas."""

        if value != OUTPUT_LABELS:
            raise ValueError("output_labels no coincide con las categorías válidas.")
        return value

    @field_validator("model_version")
    @classmethod
    def validate_model_version(cls, value: str) -> str:
        """Rechaza versiones vacías o compuestas solo por espacios."""

        if not value.strip():
            raise ValueError("model_version no puede estar vacío.")
        return value


@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


def _require_estimator(estimator: Any) -> WineQualityEstimator:
    """Comprueba la interfaz pública mínima antes de guardar o inferir."""

    if not callable(getattr(estimator, "predict", None)) or not callable(
        getattr(estimator, "predict_proba", None)
    ):
        raise ValueError("El estimador debe exponer predict y predict_proba.")
    return cast(WineQualityEstimator, estimator)


def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    """Crea un manifiesto compatible con el contrato de calidad de vino."""

    _require_estimator(estimator)
    return ArtifactManifest(
        schema_version=ARTIFACT_SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version=PREPROCESSING_VERSION,
        feature_names=FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
    )


def _atomic_write(path: Path, writer: Callable[[Path], None]) -> None:
    """Escribe un fichero temporal y lo mueve al destino solo al terminar."""

    path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    os.close(file_descriptor)
    temporary_path = Path(temporary_name)
    try:
        writer(temporary_path)
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:
    """Guarda un estimador y su manifiesto en un directorio reproducible."""

    validated_estimator = _require_estimator(estimator)
    validated_manifest = manifest or create_manifest(
        validated_estimator, model_version="unknown"
    )

    if tuple(validated_manifest.feature_names) != FEATURE_NAMES:
        raise ValueError("El manifiesto no coincide con el preprocesado.")

    if type(validated_estimator).__name__ != validated_manifest.estimator_type:
        raise ValueError("El tipo del estimador no coincide con el manifiesto.")

    model_path = bundle_path / MODEL_FILENAME
    manifest_path = bundle_path / MANIFEST_FILENAME

    _atomic_write(
        model_path,
        lambda path: joblib.dump(
            {"estimator": validated_estimator},
            path,
            compress=3,
        ),
    )
    _atomic_write(
        manifest_path,
        lambda path: path.write_text(
            validated_manifest.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        ),
    )
    return validated_manifest


def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """Valida el manifiesto y carga el estimador compatible."""

    manifest_path = bundle_path / MANIFEST_FILENAME
    model_path = bundle_path / MODEL_FILENAME
    if not manifest_path.is_file() or not model_path.is_file():
        raise FileNotFoundError(
            f"El bundle debe contener {MANIFEST_FILENAME} y {MODEL_FILENAME}: "
            f"{bundle_path}"
        )

    try:
        manifest = ArtifactManifest.model_validate_json(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, ValidationError, ValueError) as error:
        raise ValueError(f"manifest.json inválido: {error}") from error

    payload = joblib.load(model_path)
    if not isinstance(payload, Mapping):
        raise ValueError("model.joblib debe contener un mapa con estimator.")
    estimator = payload.get("estimator")
    if type(estimator).__name__ != manifest.estimator_type:
        raise ValueError("El tipo del estimador no coincide con el manifiesto.")
    return LoadedModelBundle(
        estimator=_require_estimator(estimator),
        manifest=manifest,
    )


def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """Preprocesa, infiere y valida la respuesta del estimador."""

    features = preprocess_wine_request(request)
    matrix = [features.as_vector()]
    predicted_labels = bundle.estimator.predict(matrix)
    probabilities = bundle.estimator.predict_proba(matrix)

    if len(predicted_labels) != 1 or len(probabilities) != 1:
        raise ValueError("El estimador debe devolver una salida por fila.")
    probability_row = probabilities[0]
    if len(probability_row) == 0:
        raise ValueError("El estimador no devolvió probabilidades.")

    try:
        values = [float(value) for value in probability_row]
        if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values):
            raise ValueError("Las probabilidades deben ser finitas y estar en [0, 1].")
        return WineQualityPrediction(
            quality_band=str(predicted_labels[0]),
            confidence=max(values),
            model_version=bundle.manifest.model_version,
            preprocessing_version=bundle.manifest.preprocessing_version,
        )
    except (TypeError, ValueError, ValidationError) as error:
        raise ValueError(
            f"La salida del modelo no cumple el contrato: {error}"
        ) from error
