from dataclasses import dataclass

from model_inference.contracts import WineQualityRequest

# Este contrato se entrega ya decidido: no cambies ni los nombres ni el orden.
FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)

PREPROCESSING_VERSION = "wine-red-features-v1"


@dataclass
class WineFeatures:
    values: list[float]
    preprocessing_version: str = PREPROCESSING_VERSION

    def as_vector(self):
        return self.values.copy()


def preprocess_wine_request(request: WineQualityRequest):
    # Busco cada dato por su nombre, no por su posición en el CSV.
    # No escalo ni relleno datos: solo ordeno los valores ya validados.
    values = []
    for name in FEATURE_NAMES:
        values.append(getattr(request, name))
    return WineFeatures(values)
