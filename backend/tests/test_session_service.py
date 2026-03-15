from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import anyio
from bson import ObjectId

from app.services.session import SessionService


class FakeCursor:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = [document.copy() for document in documents]

    def sort(self, key: str, direction: int) -> "FakeCursor":
        reverse = direction < 0
        self.documents.sort(key=lambda document: document.get(key), reverse=reverse)
        return self

    def limit(self, value: int) -> "FakeCursor":
        self.documents = self.documents[:value]
        return self

    async def to_list(self, _: Any) -> list[dict[str, Any]]:
        return [document.copy() for document in self.documents]


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def insert_one(self, document: dict[str, Any]) -> SimpleNamespace:
        stored = document.copy()
        stored.setdefault("_id", ObjectId())
        self.documents.append(stored)
        return SimpleNamespace(inserted_id=stored["_id"])

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document.copy()
        return None

    def find(self, query: dict[str, Any]) -> FakeCursor:
        return FakeCursor(
            [
                document
                for document in self.documents
                if all(document.get(key) == value for key, value in query.items())
            ]
        )


class FakeDatabase:
    def __init__(self) -> None:
        self.sessions = FakeCollection()
        self.chat_history = FakeCollection()
        self.business_context = FakeCollection()


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.ttl_by_key: dict[str, int] = {}

    async def get(self, key: str) -> str | None:
        return self.store.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value
        self.ttl_by_key[key] = ttl

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self.store:
                del self.store[key]
                self.ttl_by_key.pop(key, None)
                deleted += 1
        return deleted

    async def scan_iter(self, match: str):
        prefix = match[:-1] if match.endswith("*") else match
        for key in list(self.store):
            if key.startswith(prefix):
                yield key


class FakeEmbeddingService:
    calls = 0

    def __init__(self, db: FakeDatabase) -> None:
        self.db = db

    async def search(self, *, query: str, session_id: str, limit: int = 5) -> list[dict[str, Any]]:
        self.__class__.calls += 1
        assert query == "pricing feedback"
        assert session_id
        assert limit == 2
        return [
            {
                "text": "Enterprise buyers compare seat tiers before they ask for discounts.",
                "source": "document:brief.pdf",
                "score": 0.92,
                "created_at": "2026-03-15T09:00:00+00:00",
                "source_type": "document",
            },
            {
                "text": "Founder note: expansion conversations reopen on packaging complexity.",
                "source": "text:Founder notes",
                "score": 0.84,
                "created_at": "2026-03-15T09:05:00+00:00",
                "source_type": "text",
            },
        ]


def add_session(fake_db: FakeDatabase, *, user_id: str = "user-1") -> str:
    session_id = ObjectId()
    fake_db.sessions.documents.append(
        {
            "_id": session_id,
            "user_id": user_id,
            "title": "Research thread",
            "description": None,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "is_archived": False,
            "message_count": 3,
        }
    )
    return str(session_id)


def test_get_session_context_assembles_history_context_and_cache() -> None:
    fake_db = FakeDatabase()
    fake_redis = FakeRedis()
    session_id = add_session(fake_db)
    base_time = datetime(2026, 3, 15, 9, 0, tzinfo=UTC)

    fake_db.chat_history.documents.extend(
        [
            {
                "_id": ObjectId(),
                "session_id": session_id,
                "user_id": "user-1",
                "role": "user",
                "content": "What objections are showing up?",
                "timestamp": base_time,
            },
            {
                "_id": ObjectId(),
                "session_id": session_id,
                "user_id": "user-1",
                "role": "assistant",
                "content": "Buyers are pushing back on pricing transparency.",
                "timestamp": base_time + timedelta(minutes=1),
            },
            {
                "_id": ObjectId(),
                "session_id": session_id,
                "user_id": "user-1",
                "role": "user",
                "content": "Focus on packaging friction too.",
                "timestamp": base_time + timedelta(minutes=2),
            },
        ]
    )
    fake_db.business_context.documents.extend(
        [
            {
                "_id": ObjectId(),
                "session_id": session_id,
                "user_id": "user-1",
                "source_type": "document",
                "source": "brief.pdf",
                "chunk_count": 3,
                "created_at": base_time,
            },
            {
                "_id": ObjectId(),
                "session_id": session_id,
                "user_id": "user-1",
                "source_type": "url",
                "source": "https://example.com/pricing",
                "chunk_count": 2,
                "created_at": base_time + timedelta(minutes=1),
            },
            {
                "_id": ObjectId(),
                "session_id": session_id,
                "user_id": "user-1",
                "source_type": "text",
                "source": "Founder notes",
                "chunk_count": 1,
                "created_at": base_time + timedelta(minutes=2),
            },
        ]
    )

    FakeEmbeddingService.calls = 0
    service = SessionService(
        fake_db,
        redis_client=fake_redis,
        embedding_service_cls=FakeEmbeddingService,
    )

    context = anyio.run(
        lambda: service.get_session_context(
            session_id=session_id,
            user_id="user-1",
            query="pricing feedback",
            max_history=2,
            context_limit=2,
        )
    )

    assert [message["role"] for message in context["conversation_history"]] == ["assistant", "user"]
    assert context["conversation_history"][0]["content"] == "Buyers are pushing back on pricing transparency."
    assert context["recent_insights"][0]["content"] == "Buyers are pushing back on pricing transparency."
    assert context["business_context"]["documents"] == ["brief.pdf"]
    assert context["business_context"]["urls"] == ["https://example.com/pricing"]
    assert context["business_context"]["text_snippets"] == ["Founder notes"]
    assert context["business_context"]["total_chunks"] == 6
    assert len(context["business_context"]["relevant_chunks"]) == 2
    assert "Recent conversation history:" in context["formatted_context"]
    assert "Relevant business context:" in context["formatted_context"]
    assert FakeEmbeddingService.calls == 1

    assert len(fake_redis.store) == 1
    cached_key = next(iter(fake_redis.store))
    assert fake_redis.ttl_by_key[cached_key] == 3600


def test_get_session_context_uses_cache_and_invalidation() -> None:
    fake_db = FakeDatabase()
    fake_redis = FakeRedis()
    session_id = add_session(fake_db)
    fake_db.chat_history.documents.append(
        {
            "_id": ObjectId(),
            "session_id": session_id,
            "user_id": "user-1",
            "role": "assistant",
            "content": "Cached insight",
            "timestamp": datetime(2026, 3, 15, 9, 0, tzinfo=UTC),
        }
    )

    FakeEmbeddingService.calls = 0
    service = SessionService(
        fake_db,
        redis_client=fake_redis,
        embedding_service_cls=FakeEmbeddingService,
    )

    first_context = anyio.run(
        lambda: service.get_session_context(
            session_id=session_id,
            user_id="user-1",
            query="pricing feedback",
            context_limit=2,
        )
    )
    second_context = anyio.run(
        lambda: service.get_session_context(
            session_id=session_id,
            user_id="user-1",
            query="pricing feedback",
            context_limit=2,
        )
    )

    assert first_context == second_context
    assert FakeEmbeddingService.calls == 1
    assert len(fake_redis.store) == 1

    anyio.run(lambda: service.invalidate_context_cache(session_id))
    assert fake_redis.store == {}
