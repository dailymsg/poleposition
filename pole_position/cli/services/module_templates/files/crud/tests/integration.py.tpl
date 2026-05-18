from fastapi.testclient import TestClient


def test_{{module_name}}_crud_flow(client: TestClient) -> None:
    create_response = client.post("/api/v1/{{module_name}}/", json={"name": "Main {{class_name}}"})
    assert create_response.status_code == 201
    created = create_response.json()

    get_response = client.get(f"/api/v1/{{module_name}}/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Main {{class_name}}"

    update_response = client.patch(
        f"/api/v1/{{module_name}}/{created['id']}",
        json={"name": "Updated {{class_name}}"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated {{class_name}}"

    list_response = client.get("/api/v1/{{module_name}}/")
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Updated {{class_name}}"

    delete_response = client.delete(f"/api/v1/{{module_name}}/{created['id']}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/{{module_name}}/{created['id']}")
    assert missing_response.status_code == 404
