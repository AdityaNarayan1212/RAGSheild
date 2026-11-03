"""Small, non-sensitive settings shared by the local application."""

import math
import os
from pathlib import Path
from typing import Literal

APP_TITLE = "RAGShield API"
HEALTH_STATUS = "ok"
Role = Literal["employee", "hr"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RetrievalConfigurationError(ValueError):
    """Raised when the optional semantic relevance cutoff is invalid."""


def get_max_cosine_distance() -> float | None:
    """Read an optional Chroma cosine-distance cutoff from the environment."""
    raw_value = os.getenv("RAGSHIELD_MAX_COSINE_DISTANCE", "").strip()
    if not raw_value:
        return None

    try:
        value = float(raw_value)
    except ValueError as error:
        raise RetrievalConfigurationError(
            "RAGSHIELD_MAX_COSINE_DISTANCE must be a number from 0 to 2."
        ) from error

    if not math.isfinite(value) or not 0 <= value <= 2:
        raise RetrievalConfigurationError(
            "RAGSHIELD_MAX_COSINE_DISTANCE must be a number from 0 to 2."
        )
    return value
