from fastapi.testclient import TestClient

from app.main import app


def indexed_client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("RAGSHIELD_EMPLOYEE_TOKEN", "employee-vector-test")
    monkeypatch.setenv("RAGSHIELD_HR_TOKEN", "hr-vector-test")
    monkeypatch.setenv("RAGSHIELD_AUDIT_LOG", str(tmp_path / "audit.jsonl"))
    monkeypatch.setenv("CHROMA_PERSIST_DIRECTORY", str(tmp_path / "chroma"))
    monkeypatch.setattr(
        "app.rag.embed_texts",
        lambda texts: [[1.0, 0.0] for _ in texts],
    )
    client = TestClient(app)
    response = client.post(
        "/documents/index",
        headers={"Authorization": "Bearer hr-vector-test"},
    )
    assert response.status_code == 200
    assert response.json() == {"document_count": 2, "chunk_count": 2}
    return client


def test_only_hr_can_index_documents(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("RAGSHIELD_EMPLOYEE_TOKEN", "employee-vector-test")
    monkeypatch.setenv("RAGSHIELD_HR_TOKEN", "hr-vector-test")
    monkeypatch.setenv("RAGSHIELD_AUDIT_LOG", str(tmp_path / "audit.jsonl"))

    response = TestClient(app).post(
        "/documents/index",
        headers={"Authorization": "Bearer employee-vector-test"},
    )

    assert response.status_code == 403


def test_employee_semantic_search_cannot_retrieve_hr_chunks(monkeypatch, tmp_path) -> None:
    client = indexed_client(monkeypatch, tmp_path)

    response = client.get(
        "/documents/semantic-search",
        params={"q": "compensation planning"},
        headers={"Authorization": "Bearer employee-vector-test"},
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results
    assert all(result["access_level"] == "employee" for result in results)
    assert all(result["source"] == "employee-handbook.md" for result in results)


def test_hr_semantic_search_can_retrieve_both_categories(monkeypatch, tmp_path) -> None:
    client = indexed_client(monkeypatch, tmp_path)

    response = client.get(
        "/documents/semantic-search",
        params={"q": "annual leave"},
        headers={"Authorization": "Bearer hr-vector-test"},
    )

    assert response.status_code == 200
    sources = {result["source"] for result in response.json()["results"]}
    assert sources == {"employee-handbook.md", "people-operations-policy.md"}


def test_employee_answer_passes_only_employee_passages_to_generation(
    monkeypatch, tmp_path
) -> None:
    client = indexed_client(monkeypatch, tmp_path)
    captured = {}

    def fake_generate(query, sources):
        captured["sources"] = sources
        return "Submit leave requests through the portal."

    monkeypatch.setattr("app.main.generate_grounded_answer", fake_generate)

    response = client.post(
        "/documents/answer",
        json={"query": "Where do I request leave?"},
        headers={"Authorization": "Bearer employee-vector-test"},
    )

    assert response.status_code == 200
    assert captured["sources"]
    assert all(source["access_level"] == "employee" for source in captured["sources"])
    assert all(source["source"] == "employee-handbook.md" for source in captured["sources"])
    assert response.json()["sources"] == [
        {
            "title": "Employee Handbook",
            "source": "employee-handbook.md",
            "access_level": "employee",
        }
    ]
