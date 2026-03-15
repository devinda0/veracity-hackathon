from fastapi.testclient import TestClient

from app.core.app import create_app


def test_health_check_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_versioned_router_placeholder_is_mounted() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/chat/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "chat"}
