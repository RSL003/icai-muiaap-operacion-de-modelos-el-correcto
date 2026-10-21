"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

from model_packaging.artifact import DEFAULT_BUNDLE_PATH
import csv
import os
import tempfile
from model_packaging.artifact import infer_wine_quality, load_model_bundle
from model_packaging.contracts import WineQualityRequest
from model_packaging.preprocess import FEATURE_NAMES

def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    bundle = load_model_bundle(bundle_path)
    predictions = []

    with input_path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        columns = reader.fieldnames
        expected = {"sample_id", *FEATURE_NAMES}

        if not columns:
            raise ValueError("El CSV debe incluir una cabecera.")
        if len(columns) != len(set(columns)):
            raise ValueError("El CSV contiene columnas duplicadas.")
        if set(columns) != expected:
            raise ValueError("Las columnas no coinciden con el contrato.")

        for row_number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Fila {row_number}: número de valores incorrecto.")

            sample_id = row.pop("sample_id").strip()
            if not sample_id:
                raise ValueError(f"Fila {row_number} tiene un sample_id vacío.")

            try:
                request = WineQualityRequest.model_validate(row)
                prediction = infer_wine_quality(bundle, request)
            except ValueError as error:
                raise ValueError(f"Fila {row_number} inválida: {error}") from error

            predictions.append({
                "sample_id": sample_id,
                **prediction.model_dump(),
            })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(dir=output_path.parent, suffix=".tmp")
    os.close(descriptor)
    temporary_path = Path(name)

    try:
        with temporary_path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(
                target,
                fieldnames=[
                    "sample_id",
                    "quality_band",
                    "confidence",
                    "model_version",
                    "preprocessing_version",
                ],
            )
            writer.writeheader()
            writer.writerows(predictions)

        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return len(predictions)



def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    )
