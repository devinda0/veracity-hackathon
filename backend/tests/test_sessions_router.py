from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.app import create_app
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser


class FakeSessionService:
    sessions: dict[str, dict] = {}
    messages: dict[str, list[dict]] = {}
    next_id = 1

    def __init__(self, db: object) -> None:
        self.db = db

    @classmethod
    def reset(cls) -> None:
        cls.sessions = {}
        cls.messages = {}
        cls.next_id = 1

    async def create(self, user_id: str, title: str, description: str | None = None) -> dict:
        session_id = str(self.next_id)
        self.__class__.next_id += 1
        now = datetime.now(UTC)
        session = {
            "_id": session_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "created_at": now,
            "updated_at": now,
            "is_archived": False,
            "message_count": 0,
        }
        self.__class__.sessions[session_id] = session
        self.__class__.messages[session_id] = []
        return session

    async def get(self, session_id: str, user_id: str) -> dict | None:
        session = self.__class__.sessions.get(session_id)
        if session is None or session["user_id"] != user_id or session["is_archived"]:
            return None
        return session

    async def get_with_history(self, session_id: str, user_id: str) -> tuple[dict | None, list[dict]]:
        session = await self.get(session_id, user_id)
        if session is None:
            return None, []
        return session, self.__class__.messages.get(session_id, [])

    async def list_user_sessions(
        self, user_id: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[dict], int]:
        sessions = [
            session
            for session in self.__class__.sessions.values()
            if session["user_id"] == user_id and not session["is_archived"]
        ]
        sessions.sort(key=lambda session: session["updated_at"], reverse=True)
        return sessions[skip : skip + limit], len(sessions)

    async def update(
        self,
        session_id: str,
        user_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> dict | None:
        session = await self.get(session_id, user_id)
        if session is None:
            return None

        if title is not None:
            session["title"] = title
        if description is not None:
            session["description"] = description
        session["updated_at"] = datetime.now(UTC)
        return session

    async def delete(self, session_id: str, user_id: str) -> bool:
        session = await self.get(session_id, user_id)
        if session is None:
            return False

        session["is_archived"] = True
        session["updated_at"] = datetime.now(UTC)
        return True


def test_session_routes_crud_flow(monkeypatch) -> None:
    from app.routers import sessions as sessions_router

    FakeSessionService.reset()
    FakeSessionService.messages["1"] = [
        {
            "_id": "message-1",
            "role": "assistant",
            "content": "Historical context",
            "artifacts": None,
            "agent_trace": None,
            "timestamp": datetime.now(UTC),
            "tokens_used": 42,
            "cost": 0.01,
        }
    ]

    app = create_app()
    app.dependency_overrides[get_mongo_db] = lambda: object()
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(
        id="user-1",
        email="user@example.com",
        name="Test User",
    )
    monkeypatch.setattr(sessions_router, "SessionService", FakeSessionService)

    with TestClient(app) as client:
        create_response = client.post(
            "/api/v1/sessions",
            json={"title": "Competitive scan", "description": "Track active evaluations"},
        )
        assert create_response.status_code == 201
        created = create_response.json()
        assert created["title"] == "Competitive scan"
        assert created["description"] == "Track active evaluations"
        session_id = created["id"]

        FakeSessionService.messages[session_id] = [
            {
                "_id": "message-1",
                "role": "assistant",
                "content": "Historical context",
                "artifacts": None,
                "agent_trace": None,
                "timestamp": datetime.now(UTC),
                "tokens_used": 42,
                "cost": 0.01,
            }
        ]

        list_response = client.get("/api/v1/sessions")
        assert list_response.status_code == 200
        listed = list_response.json()
        assert listed["total"] == 1
        assert listed["sessions"][0]["id"] == session_id

        detail_response = client.get(f"/api/v1/sessions/{session_id}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["messages"][0]["content"] == "Historical context"

        update_response = client.put(
            f"/api/v1/sessions/{session_id}",
            json={"title": "Renamed thread", "description": "Updated scope"},
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["title"] == "Renamed thread"
        assert updated["description"] == "Updated scope"

        delete_response = client.delete(f"/api/v1/sessions/{session_id}")
        assert delete_response.status_code == 204

        empty_list_response = client.get("/api/v1/sessions")
        assert empty_list_response.status_code == 200
        assert empty_list_response.json() == {"sessions": [], "total": 0}
