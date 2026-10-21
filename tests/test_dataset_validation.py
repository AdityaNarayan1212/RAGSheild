import json

from app.documents import DOCUMENT_ROOT
from app.rag import load_indexable_documents
from scripts.validate_dataset import validate


def test_dataset_validator_accepts_isolated_phase_six_fixtures() -> None:
    assert validate() == []


def test_production_indexable_documents_exclude_security_fixture_content() -> None:
    documents = load_indexable_documents()
    fixture_path = DOCUMENT_ROOT / "security-tests" / "phase-6-fixtures.json"
    fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))["fixtures"]
    production_text = "\n".join(document.content for document in documents).casefold()

    assert documents
    assert {document.access_level for document in documents} <= {"employee", "hr"}
    for fixture in fixtures:
        assert fixture["marker"].casefold() not in production_text
        excerpt = fixture.get("excerpt")
        if excerpt:
            assert excerpt.casefold() not in production_text
