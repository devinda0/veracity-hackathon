from types import SimpleNamespace

import pytest

from app.core.app import lifespan
from app.core.app import settings as app_settings


@pytest.mark.anyio
async def test_lifespan_initializes_and_closes_datastores(monkeypatch: pytest.MonkeyPatch) -> None:
    app = SimpleNamespace(state=SimpleNamespace())
    mongo_db = object()
    qdrant_client = object()
    calls: list[str] = []
    original_env = app_settings.APP_ENV

    async def fake_connect_mongo(uri: str, database: str) -> object:
        assert uri == app_settings.MONGO_URI
        assert database == app_settings.MONGO_DATABASE
        calls.append("mongo_connect")
        return mongo_db

    async def fake_init_mongodb(db: object) -> None:
        assert db is mongo_db
        calls.append("mongo_init")

    async def fake_disconnect_mongo() -> None:
        calls.append("mongo_disconnect")

    async def fake_connect_qdrant() -> object:
        calls.append("qdrant_connect")
        return qdrant_client

    async def fake_init_qdrant(client: object) -> None:
        assert client is qdrant_client
        calls.append("qdrant_init")

    async def fake_disconnect_qdrant() -> None:
        calls.append("qdrant_disconnect")

    monkeypatch.setattr("app.core.app.MongoDBClient.connect", fake_connect_mongo)
    monkeypatch.setattr("app.core.app.init_mongodb", fake_init_mongodb)
    monkeypatch.setattr("app.core.app.MongoDBClient.disconnect", fake_disconnect_mongo)
    monkeypatch.setattr("app.core.app.QdrantClient.connect", fake_connect_qdrant)
    monkeypatch.setattr("app.core.app.init_qdrant_collections", fake_init_qdrant)
    monkeypatch.setattr("app.core.app.QdrantClient.disconnect", fake_disconnect_qdrant)

    app_settings.APP_ENV = "dev"
    try:
        async with lifespan(app):
            assert app.state.mongo_db is mongo_db
            assert app.state.qdrant_client is qdrant_client
            assert calls == ["mongo_connect", "mongo_init", "qdrant_connect", "qdrant_init"]
    finally:
        app_settings.APP_ENV = original_env

    assert calls == [
        "mongo_connect",
        "mongo_init",
        "qdrant_connect",
        "qdrant_init",
        "qdrant_disconnect",
        "mongo_disconnect",
    ]
