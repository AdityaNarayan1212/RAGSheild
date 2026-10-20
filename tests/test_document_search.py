from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def set_role_tokens(monkeypatch) -> None:
    monkeypatch.setenv("RAGSHIELD_EMPLOYEE_TOKEN", "employee-test-token")
    monkeypatch.setenv("RAGSHIELD_HR_TOKEN", "hr-test-token")


def test_search_requires_a_bearer_token(monkeypatch) -> None:
    set_role_tokens(monkeypatch)

    response = client.get("/documents/search", params={"q": "leave"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_invalid_token_is_rejected(monkeypatch) -> None:
    set_role_tokens(monkeypatch)

    response = client.get(
        "/documents/search",
        params={"q": "leave"},
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_employee_search_does_not_return_hr_documents(monkeypatch) -> None:
    set_role_tokens(monkeypatch)

    response = client.get(
        "/documents/search",
        params={"q": "annual leave compensation"},
        headers={"Authorization": "Bearer employee-test-token"},
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert results
    assert all(result["source"] == "employee-handbook.md" for result in results)
    assert all("compensation planning" not in result["snippet"] for result in results)


def test_hr_search_can_return_employee_and_hr_documents(monkeypatch) -> None:
    set_role_tokens(monkeypatch)

    response = client.get(
        "/documents/search",
        params={"q": "annual leave compensation"},
        headers={"Authorization": "Bearer hr-test-token"},
    )

    assert response.status_code == 200
    sources = {result["source"] for result in response.json()["results"]}
    assert sources == {"employee-handbook.md", "people-operations-policy.md"}


def test_role_tokens_must_be_distinct(monkeypatch) -> None:
    monkeypatch.setenv("RAGSHIELD_EMPLOYEE_TOKEN", "same-token")
    monkeypatch.setenv("RAGSHIELD_HR_TOKEN", "same-token")

    response = client.get(
        "/documents/search",
        params={"q": "leave"},
        headers={"Authorization": "Bearer same-token"},
    )

    assert response.status_code == 503
