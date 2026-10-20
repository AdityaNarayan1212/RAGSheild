"""Write minimal local JSON Lines audit events without user content or secrets."""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from app.config import Role

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_write_lock = threading.Lock()


def record_event(
    action: Literal["auth_denied", "document_search"],
    role: Role | Literal["unknown"],
    outcome: Literal["denied", "empty", "success"],
    result_count: int = 0,
) -> None:
    """Append a controlled event; caller-provided text and credentials are excluded."""
    configured_path = Path(os.getenv("RAGSHIELD_AUDIT_LOG", "logs/audit.jsonl"))
    log_path = configured_path if configured_path.is_absolute() else PROJECT_ROOT / configured_path
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "role": role,
        "outcome": outcome,
        "result_count": result_count,
    }

    with _write_lock:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(event, separators=(",", ":")) + "\n")
