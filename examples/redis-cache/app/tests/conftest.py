import pytest
from fastapi.testclient import TestClient

from redis_cache.app import create_app
from redis_cache.settings import get_settings


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("AUTH_ISSUER", "redis_cache-test")

    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
