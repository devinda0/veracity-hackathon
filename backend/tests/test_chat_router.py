from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from bson import ObjectId
from fastapi.testclient import TestClient
import pytest

from app.core.app import create_app
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.services.orchestrator import OrchestratorService
from app.websocket.manager import get_connection_manager
from app.websocket.protocol import final_message


def _reset_manager_state() -> None:
    manager = get_connection_manager()
    manager.active_connections.clear()
    manager.client_metadata.clear()
    manager.offline_queue.clear()


class FakeCursor:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = [document.copy() for document in documents]

    def sort(self, key: str, direction: int) -> "FakeCursor":
        reverse = direction < 0
        self.documents.sort(key=lambda document: document[key], reverse=reverse)
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

    async def update_one(self, query: dict[str, Any], update: dict[str, Any], upsert: bool = False) -> SimpleNamespace:
        for index, document in enumerate(self.documents):
            if not all(document.get(key) == value for key, value in query.items()):
                continue

            updated = document.copy()
            updated.update(update.get("$set", {}))
            for key, value in update.get("$inc", {}).items():
                updated[key] = updated.get(key, 0) + value
            self.documents[index] = updated
            return SimpleNamespace(matched_count=1, modified_count=1, upserted_id=None)

        if upsert:
            stored = query.copy()
            stored.update(update.get("$setOnInsert", {}))
            stored.update(update.get("$set", {}))
            stored["_id"] = stored.get("_id", ObjectId())
            self.documents.append(stored)
            return SimpleNamespace(matched_count=0, modified_count=0, upserted_id=stored["_id"])

        return SimpleNamespace(matched_count=0, modified_count=0, upserted_id=None)


class FakeDatabase:
    def __init__(self) -> None:
        self.sessions = FakeCollection()
        self.chat_history = FakeCollection()


def add_session(fake_db: FakeDatabase, *, user_id: str = "user-1", title: str = "Research") -> str:
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


class FakeRouterOrchestratorService:
    def __init__(self, db: FakeDatabase) -> None:
        self.db = db

    async def run(
        self,
        *,
        session_id: str,
        user_id: str,
        query: str,
        business_context: str | None = None,
        timeout_seconds: int = 30,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        assistant_message = {
            "_id": ObjectId(),
            "session_id": session_id,
            "user_id": user_id,
            "role": "assistant",
            "content": f"Synthesized answer for: {query}",
            "artifacts": [],
            "agent_trace": {"mode": "test"},
            "timestamp": now,
            "tokens_used": 12,
            "cost": 0.02,
        }
        await self.db.chat_history.insert_one(assistant_message)
        await self.db.sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"updated_at": now}, "$inc": {"message_count": 1}},
        )
        await get_connection_manager().broadcast(
            session_id,
            final_message(
                session_id,
                assistant_message["content"],
                agent="orchestrator",
                metadata={"trace": assistant_message["agent_trace"]},
            ),
        )
        return {
            "message_id": str(assistant_message["_id"]),
            "synthesis": assistant_message["content"],
            "artifacts": [],
            "trace": assistant_message["agent_trace"],
            "tokens_used": assistant_message["tokens_used"],
            "cost": assistant_message["cost"],
        }


class FakeEmbeddingService:
    def __init__(self, db: FakeDatabase) -> None:
        self.db = db

    async def search(self, *, query: str, session_id: str, limit: int = 3) -> list[dict[str, Any]]:
        assert query
        assert session_id
        assert limit == 3
        return [
            {
                "text": "Customers consistently compare packaging tiers before pricing.",
                "source": "document:brief.pdf",
                "score": 0.91,
                "created_at": "2026-03-15T09:00:00+00:00",
            }
        ]


@pytest.fixture
def fake_db() -> FakeDatabase:
    return FakeDatabase()


@pytest.fixture
def client(fake_db: FakeDatabase) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_mongo_db] = lambda: fake_db
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id="user-1",
        email="user@example.com",
        name="Test User",
    )
    with TestClient(app) as test_client:
        yield test_client


def test_send_message_queues_background_orchestration_and_returns_history(
    client: TestClient,
    fake_db: FakeDatabase,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.routers import chat as chat_router

    _reset_manager_state()
    monkeypatch.setattr(chat_router, "OrchestratorService", FakeRouterOrchestratorService)
    session_id = add_session(fake_db)

    response = client.post(
        "/api/v1/chat/messages",
        json={"session_id": session_id, "query": "Summarize the latest pricing objections"},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["status"] == "queued"
    assert payload["message_id"]

    assert [message["role"] for message in fake_db.chat_history.documents] == ["user", "assistant"]
    assert fake_db.sessions.documents[0]["message_count"] == 2

    queued_messages = list(get_connection_manager().offline_queue[session_id])
    assert queued_messages[-1]["type"] == "final"
    assert queued_messages[-1]["agent"] == "orchestrator"

    history_response = client.get(f"/api/v1/chat/messages/{session_id}")
    assert history_response.status_code == 200
    history = history_response.json()
    assert history["total"] == 2
    assert [message["role"] for message in history["messages"]] == ["user", "assistant"]
    assert history["messages"][1]["content"] == "Synthesized answer for: Summarize the latest pricing objections"


def test_send_message_returns_not_found_for_unknown_session(client: TestClient) -> None:
    _reset_manager_state()

    response = client.post(
        "/api/v1/chat/messages",
        json={"session_id": str(ObjectId()), "query": "Hello"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Session not found",
        "error_code": "NOT_FOUND",
    }


def test_orchestrator_service_streams_status_artifact_and_final(fake_db: FakeDatabase) -> None:
    _reset_manager_state()
    session_id = add_session(fake_db)

    service = OrchestratorService(
        fake_db,
        manager=get_connection_manager(),
        embedding_service_cls=FakeEmbeddingService,
    )

    import anyio

    result = anyio.run(
        lambda: service.run(
            session_id=session_id,
            user_id="user-1",
            query="What patterns show up in packaging feedback?",
        )
    )

    assert "Research request received" in result["synthesis"]
    assert result["artifacts"][0]["type"] == "context_snippets"
    assert fake_db.sessions.documents[0]["message_count"] == 1
    assert fake_db.chat_history.documents[0]["role"] == "assistant"

    queued_messages = list(get_connection_manager().offline_queue[session_id])
    assert [message["type"] for message in queued_messages] == [
        "status",
        "status",
        "artifact",
        "status",
        "final",
    ]
    assert queued_messages[2]["content"] == "context_snippets"
    assert queued_messages[-1]["agent"] == "orchestrator"


def test_websocket_path_endpoint_accepts_session_in_path() -> None:
    _reset_manager_state()
    client = TestClient(create_app())

    with client.websocket_connect("/api/v1/ws/chat/session-path-1") as websocket:
        connected_message = websocket.receive_json()
        assert connected_message["type"] == "status"
        assert connected_message["session_id"] == "session-path-1"
