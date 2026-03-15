import pytest

from app.db.init import init_mongodb
from app.db.mongo import MongoDBClient


class FakeCollection:
    def __init__(self) -> None:
        self.indexes: list[tuple[object, dict]] = []

    async def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))


class FakeDatabase:
    def __init__(self, existing: list[str] | None = None) -> None:
        self._existing = existing or []
        self.created: list[str] = []
        self.users = FakeCollection()
        self.sessions = FakeCollection()
        self.chat_history = FakeCollection()
        self.audit_logs = FakeCollection()
        self.business_context = FakeCollection()
        self.url_cache = FakeCollection()
        self.url_ingestions = FakeCollection()

    async def list_collection_names(self):
        return self._existing

    async def create_collection(self, name: str):
        self.created.append(name)


@pytest.mark.anyio
async def test_init_mongodb_creates_missing_collections_and_indexes() -> None:
    db = FakeDatabase(existing=["users"])

    await init_mongodb(db)

    assert db.created == ["sessions", "chat_history", "audit_logs", "business_context", "url_cache", "url_ingestions"]
    assert db.users.indexes == [("email", {"unique": True})]
    assert db.sessions.indexes == [([("user_id", 1), ("created_at", -1)], {})]
    assert db.chat_history.indexes == [([("session_id", 1), ("timestamp", -1)], {})]
    assert db.audit_logs.indexes == [([("user_id", 1), ("action", 1), ("created_at", -1)], {})]
    assert db.business_context.indexes == [([("session_id", 1), ("created_at", -1)], {})]
    assert db.url_cache.indexes == [("url_hash", {"unique": True})]
    assert db.url_ingestions.indexes == [([("user_id", 1), ("session_id", 1), ("url_hash", 1)], {"unique": True})]


def test_get_db_raises_when_mongo_not_initialized() -> None:
    MongoDBClient._db = None

    with pytest.raises(RuntimeError, match="MongoDB not initialized"):
        MongoDBClient.get_db()
