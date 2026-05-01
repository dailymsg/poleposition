from fastapi.testclient import TestClient


def test_profile_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/profile/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_profile_returns_current_user(client: TestClient, auth_token: str) -> None:
    response = client.get(
        "/api/v1/profile/me",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["subject"] == "driver-1"
    assert payload["email"] == "driver@example.com"
    assert payload["roles"] == ["member"]


def test_admin_preview_requires_admin_role(client: TestClient, auth_token: str) -> None:
    response = client.get(
        "/api/v1/profile/admin-preview",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to access this resource."


def test_admin_preview_allows_admin_role(client: TestClient, admin_token: str) -> None:
    response = client.get(
        "/api/v1/profile/admin-preview",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["roles"] == ["admin", "member"]
