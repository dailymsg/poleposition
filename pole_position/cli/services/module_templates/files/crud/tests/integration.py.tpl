from fastapi.testclient import TestClient
{{integration_auth_import}}{{integration_auth_helpers}}


def test_{{module_name}}_crud_flow(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/{{module_name}}/",
        json={{integration_create_payload}},
{{integration_headers_argument}}    )
    assert create_response.status_code == 201
    created = create_response.json()
{{integration_timestamp_assertions}}
    get_response = client.get(
        f"/api/v1/{{module_name}}/{created['id']}{{integration_item_query_suffix}}",
{{integration_headers_argument}}    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Main {{class_name}}"

    update_response = client.patch(
        f"/api/v1/{{module_name}}/{created['id']}{{integration_item_query_suffix}}",
        json={{integration_update_payload}},
{{integration_headers_argument}}    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated {{class_name}}"

    list_response = client.get(
        "/api/v1/{{module_name}}/{{integration_list_query_suffix}}",
{{integration_headers_argument}}    )
    assert list_response.status_code == 200
{{integration_list_assertions}}
    delete_response = client.delete(
        f"/api/v1/{{module_name}}/{created['id']}{{integration_item_query_suffix}}",
{{integration_headers_argument}}    )

    assert delete_response.status_code == 204

    missing_response = client.get(
        f"/api/v1/{{module_name}}/{created['id']}{{integration_item_query_suffix}}",
{{integration_headers_argument}}    )
    assert missing_response.status_code == 404
{{integration_soft_delete_assertions}}{{integration_auth_required_test}}
