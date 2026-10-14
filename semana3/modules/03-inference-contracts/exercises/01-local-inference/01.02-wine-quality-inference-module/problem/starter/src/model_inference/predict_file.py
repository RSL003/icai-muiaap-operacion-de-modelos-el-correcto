"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.
import argparse
import csv
import sys
from pathlib import Path

from .contracts import WineQualityPrediction, WineQualityRequest
from .inference import (
    DEFAULT_MODEL_PATH,
    infer_wine_quality,
    load_wine_quality_model,
)
from .preprocess import PREPROCESSING_VERSION, preprocess_wine_request


OUTPUT_COLUMNS = (
    "sample_id",
    "quality_band",
    "confidence",
    "model_version",
    "preprocessing_version",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inferencia de calidad de vino."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()

    try:
        model = load_wine_quality_model(args.model)
        predictions = []

        with args.input.open(newline="", encoding="utf-8") as source:
            reader = csv.DictReader(source)

            for line_number, row in enumerate(reader, start=2):
                sample_id = row.pop("sample_id", None)

                try:
                    if (
                        not isinstance(sample_id, str)
                        or not sample_id.strip()
                    ):
                        raise ValueError(
                            "sample_id debe ser un texto no vacío."
                        )

                    if None in row:
                        raise ValueError(
                            "La fila tiene más valores que columnas."
                        )

                    request = WineQualityRequest.model_validate(row)
                    features = preprocess_wine_request(request)
                    category, confidence = infer_wine_quality(
                        model, features
                    )

                    prediction = WineQualityPrediction(
                        quality_band=category,
                        confidence=confidence,
                        model_version=model.model_version,
                        preprocessing_version=PREPROCESSING_VERSION,
                    )

                    predictions.append(
                        {
                            "sample_id": sample_id,
                            **prediction.model_dump(),
                        }
                    )

                except (ValueError, TypeError) as error:
                    raise ValueError(
                        f"Fila {line_number}, muestra {sample_id!r}: "
                        f"{error}"
                    ) from error

        # Escribir solamente después de validar todas las filas.
        args.output.parent.mkdir(parents=True, exist_ok=True)

        with args.output.open(
            "w", newline="", encoding="utf-8"
        ) as target:
            writer = csv.DictWriter(
                target,
                fieldnames=OUTPUT_COLUMNS,
            )
            writer.writeheader()
            writer.writerows(predictions)

        print(
            f"Guardadas {len(predictions)} predicciones en {args.output}"
        )
        return 0

    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())