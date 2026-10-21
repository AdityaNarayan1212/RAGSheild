"""Validate the local synthetic corpus and confirm security fixtures stay isolated."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.documents import DOCUMENT_ROOT
from app.rag import load_indexable_documents


def validate() -> list[str]:
    errors: list[str] = []
    fixture_path = DOCUMENT_ROOT / "security-tests" / "phase-6-fixtures.json"
    try:
        fixture_data = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"Could not read the synthetic security fixtures: {error}"]

    fixtures = fixture_data.get("fixtures") if isinstance(fixture_data, dict) else None
    if not isinstance(fixtures, list) or not fixtures:
        return ["The security fixture file must contain a non-empty fixtures list."]

    fixture_payloads: list[str] = []
    fixture_ids: set[str] = set()
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            errors.append("Each security fixture must be a JSON object.")
            continue
        fixture_id = fixture.get("id")
        marker = fixture.get("marker")
        if not isinstance(fixture_id, str) or not fixture_id:
            errors.append("Each security fixture must have a non-empty id.")
        elif fixture_id in fixture_ids:
            errors.append(f"Duplicate security fixture id: {fixture_id}.")
        else:
            fixture_ids.add(fixture_id)
        if not isinstance(marker, str) or not marker:
            errors.append(f"Fixture {fixture_id or '<unknown>'} has no marker.")
        else:
            fixture_payloads.append(marker)
        excerpt = fixture.get("excerpt")
        if isinstance(excerpt, str) and excerpt:
            fixture_payloads.append(excerpt)

    documents = load_indexable_documents()
    for document in documents:
        if document.access_level not in {"employee", "hr"}:
            errors.append(f"Unexpected indexable category: {document.access_level}.")
        for payload in fixture_payloads:
            if payload.casefold() in document.content.casefold():
                errors.append(f"Security fixture marker appears in indexable source {document.source}.")

    if not fixture_path.is_file() or fixture_path.parent.name != "security-tests":
        errors.append("Security fixtures must remain in the dedicated security-tests directory.")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Dataset validation passed: security fixtures are separate from indexable employee and HR sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
