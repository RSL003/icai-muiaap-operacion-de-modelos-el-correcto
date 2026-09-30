import argparse
import csv
from pathlib import Path

from model_inference.contracts import WineQualityRequest
from model_inference.inference import (
    DEFAULT_MODEL_PATH,
    infer_wine_quality,
    load_wine_quality_model,
)
from model_inference.preprocess import preprocess_wine_request


def predict_file(input_path, output_path, model_path=DEFAULT_MODEL_PATH):
    model = load_wine_quality_model(model_path)
    predictions = []

    with Path(input_path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        for row in reader:
            # El identificador acompaña a la respuesta, pero no entra al modelo.
            sample_id = row.pop("sample_id", "")
            try:
                if not sample_id or not sample_id.strip():
                    raise ValueError("sample_id no puede estar vacío")
                request = WineQualityRequest.model_validate(row)
                features = preprocess_wine_request(request)
                prediction = infer_wine_quality(features, model, sample_id)
                predictions.append(prediction.model_dump())
            except (ValueError, TypeError) as error:
                raise ValueError(f"Muestra {sample_id}: {error}") from error

    if not predictions:
        raise ValueError("El CSV no contiene muestras")

    # Abrimos la salida solamente cuando todas las filas han salido bien.
    # Si falla la segunda fila, no se guarda ni siquiera la primera.
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as target:
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
    return len(predictions)


def main():
    parser = argparse.ArgumentParser(
        description="Predecir la calidad de muestras de vino"
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path)
    args = parser.parse_args()

    try:
        count = predict_file(args.input, args.output, args.model)
    except (OSError, ValueError, TypeError, EOFError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Guardadas {count} predicciones en {args.output}")


if __name__ == "__main__":
    main()
