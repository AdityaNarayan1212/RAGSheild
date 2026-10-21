import json

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def configure_test_environment(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("RAGSHIELD_EMPLOYEE_TOKEN", "employee-answer-test")
    monkeypatch.setenv("RAGSHIELD_HR_TOKEN", "hr-answer-test")
    monkeypatch.setenv("RAGSHIELD_AUDIT_LOG", str(tmp_path / "audit.jsonl"))


def test_answer_uses_role_filtered_sources_and_logs_no_user_content(
    monkeypatch, tmp_path
) -> None:
    configure_test_environment(monkeypatch, tmp_path)
    employee_result = {
        "title": "Employee handbook",
        "source": "employee-handbook.md",
        "access_level": "employee",
        "snippet": "Employees submit leave requests through the portal.",
        "distance": 0.1,
    }
    hr_result = {
        "title": "People operations policy",
        "source": "people-operations-policy.md",
        "access_level": "hr",
        "snippet": "HR-only compensation planning details.",
        "distance": 0.2,
    }
    requested = {}
    generated = {}

    def fake_search(query, role, limit):
        requested.update(query=query, role=role, limit=limit)
        return [employee_result] if role == "employee" else [employee_result, hr_result]

    def fake_generate(query, sources):
        generated.update(query=query, sources=sources)
        return "Submit a request through the portal."

    monkeypatch.setattr("app.main.semantic_search", fake_search)
    monkeypatch.setattr("app.main.generate_grounded_answer", fake_generate)
    query = "How do I request leave?"

    response = client.post(
        "/documents/answer",
        json={"query": query},
        headers={"Authorization": "Bearer employee-answer-test"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Submit a request through the portal.",
        "sources": [
            {
                "title": "Employee handbook",
                "source": "employee-handbook.md",
                "access_level": "employee",
            }
        ],
    }
    assert requested == {"query": query, "role": "employee", "limit": 5}
    assert generated["sources"] == [employee_result]

    log_path = tmp_path / "audit.jsonl"
    events = [
        json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()
    ]
    assert events[0]["action"] == "document_answer"
    assert events[0]["role"] == "employee"
    assert events[0]["result_count"] == 1
    log_text = log_path.read_text(encoding="utf-8")
    assert query not in log_text
    assert "employee-answer-test" not in log_text
    assert "employee-handbook.md" not in log_text
    assert "people-operations-policy.md" not in log_text


def test_answer_without_retrieval_skips_generation(monkeypatch, tmp_path) -> None:
    configure_test_environment(monkeypatch, tmp_path)
    monkeypatch.setattr("app.main.semantic_search", lambda query, role, limit: [])

    def fail_generation(query, sources):
        raise AssertionError("Generation should be skipped when retrieval is empty.")

    monkeypatch.setattr("app.main.generate_grounded_answer", fail_generation)

    response = client.post(
        "/documents/answer",
        json={"query": "A question with no matches"},
        headers={"Authorization": "Bearer employee-answer-test"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "I couldn't find relevant information in the available documents.",
        "sources": [],
    }
    event = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8").strip())
    assert event["outcome"] == "empty"
    assert event["result_count"] == 0


def test_answer_requires_authentication(monkeypatch, tmp_path) -> None:
    configure_test_environment(monkeypatch, tmp_path)

    response = client.post("/documents/answer", json={"query": "Question?"})

    assert response.status_code == 401


def test_answer_returns_service_unavailable_when_local_ollama_fails(
    monkeypatch, tmp_path
) -> None:
    configure_test_environment(monkeypatch, tmp_path)
    monkeypatch.setattr(
        "app.main.semantic_search",
        lambda query, role, limit: [
            {
                "title": "Employee handbook",
                "source": "employee-handbook.md",
                "access_level": "employee",
                "snippet": "Relevant content.",
                "distance": 0.1,
            }
        ],
    )

    def fail_generation(query, sources):
        from app.ollama import OllamaUnavailable

        raise OllamaUnavailable("Local model unavailable.")

    monkeypatch.setattr("app.main.generate_grounded_answer", fail_generation)
    response = client.post(
        "/documents/answer",
        json={"query": "Question?"},
        headers={"Authorization": "Bearer employee-answer-test"},
    )

    assert response.status_code == 503
