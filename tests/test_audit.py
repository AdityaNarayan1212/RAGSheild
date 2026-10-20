import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def configure_test_environment(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("RAGSHIELD_EMPLOYEE_TOKEN", "employee-secret-for-test")
    monkeypatch.setenv("RAGSHIELD_HR_TOKEN", "hr-secret-for-test")
    monkeypatch.setenv("RAGSHIELD_AUDIT_LOG", str(tmp_path / "audit.jsonl"))


def read_events(path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_search_audit_records_metadata_without_query_or_secret(monkeypatch, tmp_path) -> None:
    configure_test_environment(monkeypatch, tmp_path)
    query = "leave query that should not appear in logs"

    response = client.get(
        "/documents/search",
        params={"q": query},
        headers={"Authorization": "Bearer employee-secret-for-test"},
    )

    assert response.status_code == 200
    log_path = tmp_path / "audit.jsonl"
    events = read_events(log_path)
    assert len(events) == 1
    assert events[0]["action"] == "document_search"
    assert events[0]["role"] == "employee"
    assert events[0]["outcome"] == "success"
    assert events[0]["result_count"] == 1
    log_text = log_path.read_text(encoding="utf-8")
    assert query not in log_text
    assert "employee-secret-for-test" not in log_text
    assert "employee-handbook.md" not in log_text


def test_denied_authentication_is_audited_without_token(monkeypatch, tmp_path) -> None:
    configure_test_environment(monkeypatch, tmp_path)

    response = client.get(
        "/documents/search",
        params={"q": "leave"},
        headers={"Authorization": "Bearer invalid-secret-for-test"},
    )

    assert response.status_code == 401
    log_path = tmp_path / "audit.jsonl"
    events = read_events(log_path)
    assert len(events) == 1
    assert events[0]["action"] == "auth_denied"
    assert events[0]["role"] == "unknown"
    assert "invalid-secret-for-test" not in log_path.read_text(encoding="utf-8")
