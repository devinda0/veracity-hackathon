from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from bson import ObjectId
from fastapi.testclient import TestClient
import pytest

from app.core.app import create_app
from app.core.security import create_access_token, hash_password
from app.db.mongo import MongoDBClient


class FakeUsersCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document.copy()
        return None


class FakeCollectionCursor:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = list(documents)

    def sort(self, key: str, direction: int) -> "FakeCollectionCursor":
        reverse = direction < 0
        self.documents.sort(key=lambda document: document.get(key) or datetime.min.replace(tzinfo=UTC), reverse=reverse)
        return self

    async def to_list(self, _: int | None) -> list[dict[str, Any]]:
        return [document.copy() for document in self.documents]


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document.copy()
        return None

    async def insert_one(self, document: dict[str, Any]) -> SimpleNamespace:
        stored = document.copy()
        stored["_id"] = ObjectId()
        self.documents.append(stored)
        return SimpleNamespace(inserted_id=stored["_id"])

    async def update_one(self, query: dict[str, Any], update: dict[str, Any], upsert: bool = False) -> SimpleNamespace:
        for index, document in enumerate(self.documents):
            if all(document.get(key) == value for key, value in query.items()):
                updated = document.copy()
                updated.update(update.get("$set", {}))
                self.documents[index] = updated
                return SimpleNamespace(matched_count=1, upserted_id=None)

        if not upsert:
            return SimpleNamespace(matched_count=0, upserted_id=None)

        stored = query.copy()
        stored.update(update.get("$setOnInsert", {}))
        stored.update(update.get("$set", {}))
        stored["_id"] = ObjectId()
        self.documents.append(stored)
        return SimpleNamespace(matched_count=0, upserted_id=stored["_id"])

    def find(self, query: dict[str, Any]) -> FakeCollectionCursor:
        matched = [
            document.copy()
            for document in self.documents
            if all(document.get(key) == value for key, value in query.items())
        ]
        return FakeCollectionCursor(matched)


class FakeDatabase:
    def __init__(self) -> None:
        self.users = FakeUsersCollection()
        self.sessions = FakeCollection()
        self.chat_history = FakeCollection()
        self.business_context = FakeCollection()
        self.url_cache = FakeCollection()
        self.url_ingestions = FakeCollection()
        self.embedding_cache = FakeCollection()

    def __getitem__(self, collection_name: str) -> Any:
        return getattr(self, collection_name)


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


def add_session(fake_db: FakeDatabase, user_id: str, *, title: str = "Context Session") -> str:
    session_id = ObjectId()
    fake_db.sessions.documents.append(
        {
            "_id": session_id,
            "user_id": user_id,
            "title": title,
            "description": None,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "is_archived": False,
            "message_count": 0,
        }
    )
    return str(session_id)


def test_upload_context_document_indexes_and_persists(
    client: TestClient,
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.routers import context as context_router

    user = add_user(fake_db, email="founder@example.com", name="Founder")
    session_id = add_session(fake_db, str(user["_id"]))
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    class FakeEmbeddingService:
        EMBEDDING_MODEL = "fake-embedding-model"
        EMBEDDING_DIM = 3
        calls: list[dict[str, Any]] = []

        def __init__(self, db: FakeDatabase) -> None:
            assert db is fake_db

        async def index_chunks(
            self,
            chunks: list[str],
            session_id: str,
            source: str,
            *,
            collection: str = "business_context",
            metadata: dict[str, Any] | None = None,
            created_at: datetime | None = None,
        ) -> int:
            self.__class__.calls.append(
                {
                    "chunks": list(chunks),
                    "session_id": session_id,
                    "source": source,
                    "collection": collection,
                    "metadata": dict(metadata or {}),
                    "created_at": created_at,
                }
            )
            return len(chunks)

    monkeypatch.setattr(context_router, "EmbeddingService", FakeEmbeddingService)

    response = client.post(
        f"/api/v1/sessions/{session_id}/context",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("context.txt", b"Useful context for the embedding pipeline.", "text/plain")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["type"] == "document"
    assert payload["source"] == "context.txt"
    assert payload["chunk_count"] == 1
    assert payload["metadata"]["title"] == "context"
    assert payload["embedding"] == {
        "model": "fake-embedding-model",
        "dimensions": 3,
        "indexed_chunks": 1,
        "collection": "business_context",
    }

    stored = fake_db.business_context.documents[0]
    assert stored["user_id"] == str(user["_id"])
    assert stored["session_id"] == session_id
    assert stored["source_type"] == "document"
    assert stored["source"] == "context.txt"
    assert stored["chunk_count"] == 1
    assert stored["chunks"] == ["Useful context for the embedding pipeline."]

    assert FakeEmbeddingService.calls == [
        {
            "chunks": ["Useful context for the embedding pipeline."],
            "session_id": session_id,
            "source": "document:context.txt",
            "collection": "business_context",
            "metadata": {
                "source_type": "document",
                "title": "context",
                "file_type": "txt",
            },
            "created_at": stored["created_at"],
        }
    ]


def test_upload_context_rejects_oversized_file(
    client: TestClient,
    fake_db: FakeDatabase,
) -> None:
    user = add_user(fake_db)
    session_id = add_session(fake_db, str(user["_id"]))
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    response = client.post(
        f"/api/v1/sessions/{session_id}/context",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("large.txt", b"a" * (10 * 1024 * 1024 + 1), "text/plain")},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "File too large. Max 10MB."}


def test_ingest_context_url_indexes_and_deduplicates(
    client: TestClient,
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.routers import context as context_router

    user = add_user(fake_db, email="founder@example.com", name="Founder")
    session_id = add_session(fake_db, str(user["_id"]))
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    class FakeEmbeddingService:
        EMBEDDING_MODEL = "fake-embedding-model"
        EMBEDDING_DIM = 3
        calls: list[dict[str, Any]] = []

        def __init__(self, db: FakeDatabase) -> None:
            assert db is fake_db

        async def index_chunks(
            self,
            chunks: list[str],
            session_id: str,
            source: str,
            *,
            collection: str = "business_context",
            metadata: dict[str, Any] | None = None,
            created_at: datetime | None = None,
        ) -> int:
            self.__class__.calls.append(
                {
                    "chunks": list(chunks),
                    "session_id": session_id,
                    "source": source,
                    "collection": collection,
                    "metadata": dict(metadata or {}),
                }
            )
            return len(chunks)

    async def fake_ingest(self, url: str, incoming_session_id: str, user_id: str) -> dict[str, Any]:
        assert url == "https://example.com/context"
        assert incoming_session_id == session_id
        assert user_id == str(user["_id"])
        return {
            "url": url,
            "url_hash": "url-hash-123",
            "content": "Useful website context.",
            "chunks": ["Useful website context."],
            "source": "web",
            "method": "firecrawl",
            "cached": False,
        }

    monkeypatch.setattr(context_router, "EmbeddingService", FakeEmbeddingService)
    monkeypatch.setattr(context_router.URLIngestionService, "ingest_url", fake_ingest)

    first = client.post(
        f"/api/v1/sessions/{session_id}/context/url",
        headers={"Authorization": f"Bearer {token}"},
        json={"url": "https://example.com/context"},
    )

    assert first.status_code == 201
    first_payload = first.json()
    assert first_payload["type"] == "url"
    assert first_payload["source"] == "https://example.com/context"
    assert first_payload["chunk_count"] == 1
    assert first_payload["metadata"]["method"] == "firecrawl"
    assert first_payload["metadata"]["deduplicated"] is False
    assert len(fake_db.business_context.documents) == 1
    assert fake_db.url_ingestions.documents[0]["chunk_count"] == 1

    second = client.post(
        f"/api/v1/sessions/{session_id}/context/url",
        headers={"Authorization": f"Bearer {token}"},
        json={"url": "https://example.com/context"},
    )

    assert second.status_code == 201
    assert second.json()["metadata"]["deduplicated"] is True
    assert len(fake_db.business_context.documents) == 1
    assert len(FakeEmbeddingService.calls) == 2


def test_add_text_context_and_list_session_contexts(
    client: TestClient,
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.routers import context as context_router

    user = add_user(fake_db)
    session_id = add_session(fake_db, str(user["_id"]))
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    class FakeEmbeddingService:
        EMBEDDING_MODEL = "fake-embedding-model"
        EMBEDDING_DIM = 3

        def __init__(self, db: FakeDatabase) -> None:
            assert db is fake_db

        async def index_chunks(
            self,
            chunks: list[str],
            session_id: str,
            source: str,
            *,
            collection: str = "business_context",
            metadata: dict[str, Any] | None = None,
            created_at: datetime | None = None,
        ) -> int:
            return len(chunks)

    monkeypatch.setattr(context_router, "EmbeddingService", FakeEmbeddingService)

    create_response = client.post(
        f"/api/v1/sessions/{session_id}/context/text",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Founder notes", "text": "Pricing is enterprise-led and expansion revenue is growing."},
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["type"] == "text"
    assert created["source"] == "Founder notes"
    assert created["chunk_count"] == 1
    assert created["metadata"]["characters"] == 59

    fake_db.business_context.documents.append(
        {
            "_id": ObjectId(),
            "user_id": str(user["_id"]),
            "session_id": session_id,
            "source_type": "document",
            "source": "brief.pdf",
            "chunk_count": 2,
            "metadata": {"title": "Brief"},
            "created_at": datetime(2026, 3, 15, 8, 0, tzinfo=UTC),
        }
    )

    list_response = client.get(
        f"/api/v1/sessions/{session_id}/context",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload["session_id"] == session_id
    assert payload["total"] == 2
    assert payload["total_chunks"] == 3
    assert payload["contexts"][0]["source"] == "Founder notes"
    assert payload["contexts"][0]["type"] == "text"
    assert payload["contexts"][1]["source"] == "brief.pdf"
    assert payload["contexts"][1]["type"] == "document"


def test_context_routes_require_owned_session(
    client: TestClient,
    fake_db: FakeDatabase,
) -> None:
    owner = add_user(fake_db, email="owner@example.com")
    other_user = add_user(fake_db, email="other@example.com")
    session_id = add_session(fake_db, str(owner["_id"]))
    token = create_access_token({"sub": str(other_user["_id"]), "email": other_user["email"]})

    response = client.get(
        f"/api/v1/sessions/{session_id}/context",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}
