"""Small, non-sensitive settings shared by the local application."""

from pathlib import Path
from typing import Literal

APP_TITLE = "RAGShield API"
HEALTH_STATUS = "ok"
Role = Literal["employee", "hr"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
