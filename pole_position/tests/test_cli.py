from fastapi.testclient import TestClient

from {{project_name}} import __version__
from {{project_name}}.app import app

client = TestClient(app)


def test_version_exists() -> None:
    assert isinstance(__version__, str)
    assert __version__


def test_status() -> None:
    response = client.get("/api/v1/status")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "{{project_name}}"
    assert payload["version"] == __version__