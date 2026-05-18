from fastapi.testclient import TestClient


def test_register_login_and_me(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "correct horse"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "user@example.com"

    token_response = client.post(
        "/api/v1/auth/token",
        json={"email": "user@example.com", "password": "correct horse"},
    )
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "user@example.com"
