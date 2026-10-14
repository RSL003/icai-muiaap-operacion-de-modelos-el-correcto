"""TODO: transformación de una muestra validada en el vector del modelo."""

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

# Implementa WineFeatures y preprocess_wine_request(). El orden anterior debe
# coincidir con el artefacto, no con un orden arbitrario del CSV.
from dataclasses import dataclass
from .contracts import WineQualityRequest

PREPROCESSING_VERSION = "wine-red-features-v1"


@dataclass(frozen=True, slots=True)
class WineFeatures:
    values: tuple[float, ...]

    def as_vector(self) -> list[float]:
        return list(self.values)


def preprocess_wine_request(request: WineQualityRequest) -> WineFeatures:
    values = tuple(getattr(request, name) for name in FEATURE_NAMES)
    return WineFeatures(values=values)