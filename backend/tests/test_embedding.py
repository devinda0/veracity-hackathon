from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from bson import ObjectId
from fastapi.testclient import TestClient
import pytest
from qdrant_client.models import MatchValue, Range

from app.core.app import create_app
from app.core.security import create_access_token, hash_password
from app.db.mongo import MongoDBClient
from app.services.embedding import EmbeddingService


class FakeUsersCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document.copy()
        return None


class FakeEmbeddingCacheCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document.copy()
        return None

    async def update_one(self, query: dict[str, Any], update: dict[str, Any], upsert: bool = False) -> SimpleNamespace:
        for index, document in enumerate(self.documents):
            if all(document.get(key) == value for key, value in query.items()):
                updated = document.copy()
                updated.update(update.get("$set", {}))
                self.documents[index] = updated
                return SimpleNamespace(matched_count=1, upserted_id=None)

        if upsert:
            stored = query.copy()
            stored.update(update.get("$setOnInsert", {}))
            stored.update(update.get("$set", {}))
            stored["_id"] = ObjectId()
            self.documents.append(stored)
            return SimpleNamespace(matched_count=0, upserted_id=stored["_id"])

        return SimpleNamespace(matched_count=0, upserted_id=None)


class FakeDatabase:
    def __init__(self) -> None:
        self.users = FakeUsersCollection()
        self.embedding_cache = FakeEmbeddingCacheCollection()

    def __getitem__(self, collection_name: str) -> Any:
        return getattr(self, collection_name)


class FakeEmbeddingAPI:
    def __init__(self, vectors_by_text: dict[str, list[float]]) -> None:
        self.vectors_by_text = vectors_by_text
        self.calls: list[dict[str, Any]] = []

    async def create(self, *, model: str, input: list[str]) -> SimpleNamespace:
        self.calls.append({"model": model, "input": list(input)})
        return SimpleNamespace(
            data=[SimpleNamespace(embedding=self.vectors_by_text[text]) for text in input]
        )


class FakeOpenAIClient:
    def __init__(self, vectors_by_text: dict[str, list[float]]) -> None:
        self.embeddings = FakeEmbeddingAPI(vectors_by_text)


class FakeQdrantClient:
    def __init__(self, search_results: list[Any] | None = None) -> None:
        self.search_results = search_results or []
        self.upserts: list[tuple[str, list[Any], bool]] = []
        self.query_calls: list[dict[str, Any]] = []

    async def upsert(self, collection_name: str, points: list[Any], wait: bool = True) -> None:
        self.upserts.append((collection_name, points, wait))

    async def query_points(
        self,
        collection_name: str,
        query: list[float],
        limit: int,
        query_filter: Any,
        with_payload: bool,
    ) -> SimpleNamespace:
        self.query_calls.append(
            {
                "collection_name": collection_name,
                "query": query,
                "limit": limit,
                "query_filter": query_filter,
                "with_payload": with_payload,
            }
        )
        return SimpleNamespace(points=self.search_results)


@pytest.fixture
def fake_db() -> FakeDatabase:
    original_db = MongoDBClient._db
    database = FakeDatabase()
    MongoDBClient._db = database
    try:
        yield database
    finally:
        MongoDBClient._db = original_db


@pytest.fixture
def client(fake_db: FakeDatabase) -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def add_user(
    fake_db: FakeDatabase,
    *,
    email: str = "user@example.com",
    password: str = "Secret123!",
    name: str = "Test User",
) -> dict[str, Any]:
    user = {
        "_id": ObjectId(),
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "is_active": True,
    }
    fake_db.users.documents.append(user)
    return user


@pytest.mark.anyio
async def test_embed_texts_uses_mongo_cache_for_repeated_inputs(fake_db: FakeDatabase) -> None:
    openai_client = FakeOpenAIClient(
        {
            "alpha": [0.1, 0.2, 0.3],
            "beta": [0.4, 0.5, 0.6],
        }
    )
    service = EmbeddingService(db=fake_db, openai_client=openai_client, qdrant_client=FakeQdrantClient())

    first = await service.embed_texts(["alpha", "beta", "alpha"])
    second = await service.embed_texts(["beta"])

    assert first == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.1, 0.2, 0.3],
    ]
    assert second == [[0.4, 0.5, 0.6]]
    assert openai_client.embeddings.calls == [
        {
            "model": EmbeddingService.EMBEDDING_MODEL,
            "input": ["alpha", "beta"],
        }
    ]
    assert len(fake_db.embedding_cache.documents) == 2


@pytest.mark.anyio
async def test_index_chunks_upserts_qdrant_points_with_metadata(fake_db: FakeDatabase) -> None:
    qdrant_client = FakeQdrantClient()
    service = EmbeddingService(
        db=fake_db,
        openai_client=FakeOpenAIClient(
            {
                "First chunk": [0.1, 0.2, 0.3],
                "Second chunk": [0.4, 0.5, 0.6],
            }
        ),
        qdrant_client=qdrant_client,
    )

    indexed = await service.index_chunks(
        ["First chunk", "Second chunk"],
        "session-123",
        "document:brief.pdf",
        metadata={"source_type": "document", "document_id": "doc-1"},
        created_at=datetime(2026, 3, 15, 9, 0, tzinfo=UTC),
    )

    assert indexed == 2
    assert len(qdrant_client.upserts) == 1
    collection_name, points, wait = qdrant_client.upserts[0]
    assert collection_name == "business_context"
    assert wait is True
    assert len(points) == 2
    assert points[0].payload == {
        "session_id": "session-123",
        "source": "document:brief.pdf",
        "source_type": "document",
        "chunk_index": 0,
        "text": "First chunk",
        "created_at": int(datetime(2026, 3, 15, 9, 0, tzinfo=UTC).timestamp()),
        "metadata": {"document_id": "doc-1"},
    }


@pytest.mark.anyio
async def test_search_filters_by_session_source_and_date(fake_db: FakeDatabase) -> None:
    qdrant_client = FakeQdrantClient(
        search_results=[
            SimpleNamespace(
                score=0.91,
                payload={
                    "text": "Pricing notes",
                    "source": "document:brief.pdf",
                    "source_type": "document",
                    "chunk_index": 0,
                    "created_at": int(datetime(2026, 3, 15, 9, 0, tzinfo=UTC).timestamp()),
                    "metadata": {"title": "Brief"},
                },
            )
        ]
    )
    service = EmbeddingService(
        db=fake_db,
        openai_client=FakeOpenAIClient({"pricing strategy": [0.7, 0.8, 0.9]}),
        qdrant_client=qdrant_client,
    )

    results = await service.search(
        "pricing strategy",
        "session-123",
        source="document:brief.pdf",
        created_after=datetime(2026, 3, 14, 0, 0, tzinfo=UTC),
        created_before=datetime(2026, 3, 16, 0, 0, tzinfo=UTC),
    )

    assert results == [
        {
            "text": "Pricing notes",
            "source": "document:brief.pdf",
            "source_type": "document",
            "score": 0.91,
            "chunk_index": 0,
            "created_at": "2026-03-15T09:00:00+00:00",
            "metadata": {"title": "Brief"},
        }
    ]

    query_call = qdrant_client.query_calls[0]
    assert query_call["collection_name"] == "business_context"
    assert query_call["query"] == [0.7, 0.8, 0.9]
    assert query_call["limit"] == 5
    assert query_call["with_payload"] is True

    must_conditions = query_call["query_filter"].must
    assert must_conditions[0].key == "session_id"
    assert must_conditions[0].match == MatchValue(value="session-123")
    assert must_conditions[1].key == "source"
    assert must_conditions[1].match == MatchValue(value="document:brief.pdf")
    assert must_conditions[2].key == "created_at"
    assert must_conditions[2].range == Range(
        gte=int(datetime(2026, 3, 14, 0, 0, tzinfo=UTC).timestamp()),
        lte=int(datetime(2026, 3, 16, 0, 0, tzinfo=UTC).timestamp()),
    )


def test_semantic_search_route_returns_results(
    client: TestClient,
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = add_user(fake_db, email="founder@example.com", name="Founder")
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    class FakeService:
        def __init__(self, db: FakeDatabase) -> None:
            assert db is fake_db

        async def search(
            self,
            query: str,
            session_id: str,
            *,
            limit: int = 5,
            collection: str = "business_context",
            source: str | None = None,
            created_after: datetime | None = None,
            created_before: datetime | None = None,
        ) -> list[dict[str, Any]]:
            assert query == "pricing"
            assert session_id == "session-123"
            assert limit == 3
            assert source == "document:brief.pdf"
            assert collection == "business_context"
            assert created_after == datetime(2026, 3, 14, 0, 0, tzinfo=UTC)
            assert created_before == datetime(2026, 3, 16, 0, 0, tzinfo=UTC)
            return [{"text": "Pricing notes", "source": source, "score": 0.92, "metadata": {}}]

    monkeypatch.setattr("app.routers.embedding.EmbeddingService", FakeService)

    response = client.post(
        "/api/v1/embedding/semantic-search",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": "pricing",
            "session_id": "session-123",
            "limit": 3,
            "source": "document:brief.pdf",
            "created_after": "2026-03-14T00:00:00Z",
            "created_before": "2026-03-16T00:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "query": "pricing",
        "session_id": "session-123",
        "results": [{"text": "Pricing notes", "source": "document:brief.pdf", "score": 0.92, "metadata": {}}],
        "total": 1,
    }
