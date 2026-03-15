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
from app.services.url_ingestion import URLIngestionError, URLIngestionService


class FakeUsersCollection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    async def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents:
            if all(document.get(key) == value for key, value in query.items()):
                return document.copy()
        return None


class FakeInsertCollection:
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
        self.business_context = FakeInsertCollection()
        self.url_cache = FakeInsertCollection()
        self.url_ingestions = FakeInsertCollection()


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
async def test_service_returns_cached_content_without_refetch(
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = URLIngestionService(fake_db)
    normalized_url = service._normalize_url("https://example.com/article/")
    fake_db.url_cache.documents.append(
        {
            "_id": ObjectId(),
            "url": normalized_url,
            "url_hash": service._url_hash(normalized_url),
            "content": "Cached web content.",
            "chunks": ["Cached web content."],
            "method": "firecrawl",
            "created_at": datetime.now(UTC),
        }
    )

    async def unexpected_fetch(url: str) -> str:
        raise AssertionError(f"should not fetch {url}")

    monkeypatch.setattr(service, "_fetch_with_firecrawl", unexpected_fetch)

    result = await service.ingest_url("https://EXAMPLE.com/article/#fragment", "session-1", "user-1")

    assert result["url"] == "https://example.com/article"
    assert result["source"] == "cache"
    assert result["method"] == "firecrawl"
    assert result["chunks"] == ["Cached web content."]


@pytest.mark.anyio
async def test_service_uses_playwright_when_firecrawl_fails(
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = URLIngestionService(fake_db)

    async def fail_firecrawl(url: str) -> str:
        raise URLIngestionError("firecrawl unavailable")

    async def playwright_content(url: str) -> str:
        assert url == "https://example.com/news"
        return "Rendered content from browser fallback."

    monkeypatch.setattr(service, "_fetch_with_firecrawl", fail_firecrawl)
    monkeypatch.setattr(service, "_fetch_with_playwright", playwright_content)

    result = await service.ingest_url("https://example.com/news/", "session-1", "user-1")

    assert result["method"] == "playwright"
    assert result["source"] == "web"
    assert result["cached"] is False
    assert result["chunks"] == ["Rendered content from browser fallback."]
    assert fake_db.url_cache.documents[0]["method"] == "playwright"


def test_ingest_url_route_persists_business_context_and_deduplicates(
    client: TestClient,
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = add_user(fake_db, email="founder@example.com", name="Founder")
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    async def fake_ingest(
        self: URLIngestionService,
        url: str,
        session_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        assert url == "https://example.com/context"
        assert session_id == "session-123"
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

    monkeypatch.setattr("app.routers.ingestion.URLIngestionService.ingest_url", fake_ingest)

    response = client.post(
        "/api/v1/ingestion/ingest-url",
        headers={"Authorization": f"Bearer {token}"},
        json={"url": "https://example.com/context", "session_id": "session-123"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["url"] == "https://example.com/context"
    assert payload["chunks"] == 1
    assert payload["source"] == "web"
    assert payload["deduplicated"] is False

    stored_context = fake_db.business_context.documents[0]
    assert stored_context["user_id"] == str(user["_id"])
    assert stored_context["session_id"] == "session-123"
    assert stored_context["source_type"] == "url"
    assert stored_context["url_hash"] == "url-hash-123"
    assert stored_context["chunks"] == ["Useful website context."]
    assert fake_db.url_ingestions.documents[0]["chunk_count"] == 1

    duplicate = client.post(
        "/api/v1/ingestion/ingest-url",
        headers={"Authorization": f"Bearer {token}"},
        json={"url": "https://example.com/context", "session_id": "session-123"},
    )

    assert duplicate.status_code == 201
    assert duplicate.json()["deduplicated"] is True
    assert len(fake_db.business_context.documents) == 1


def test_ingest_url_route_rejects_bad_source(
    client: TestClient,
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = add_user(fake_db)
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})

    async def bad_ingest(self: URLIngestionService, url: str, session_id: str, user_id: str) -> dict[str, Any]:
        raise URLIngestionError("Invalid URL")

    monkeypatch.setattr("app.routers.ingestion.URLIngestionService.ingest_url", bad_ingest)

    response = client.post(
        "/api/v1/ingestion/ingest-url",
        headers={"Authorization": f"Bearer {token}"},
        json={"url": "https://example.com", "session_id": "session-123"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid URL"}
