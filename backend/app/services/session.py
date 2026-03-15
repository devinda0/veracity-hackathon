from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logger import get_logger

logger = get_logger(__name__)


class SessionService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = db.sessions
        self.chat_history = db.chat_history

    async def create(
        self,
        user_id: str,
        title: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        session = {
            "user_id": user_id,
            "title": title.strip(),
            "description": self._normalize_description(description),
            "created_at": now,
            "updated_at": now,
            "is_archived": False,
            "message_count": 0,
        }
        result = await self.collection.insert_one(session)
        session["_id"] = result.inserted_id
        logger.info("session_created", session_id=str(result.inserted_id), user_id=user_id)
        return session

    async def get(self, session_id: str, user_id: str) -> dict[str, Any] | None:
        object_id = self._to_object_id(session_id)
        if object_id is None:
            return None

        return await self.collection.find_one(
            {
                "_id": object_id,
                "user_id": user_id,
                "is_archived": False,
            }
        )

    async def get_with_history(
        self, session_id: str, user_id: str
    ) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
        session = await self.get(session_id, user_id)
        if session is None:
            return None, []

        messages = await self.chat_history.find({"session_id": session_id}).sort("timestamp", 1).to_list(None)
        return session, messages

    async def list_user_sessions(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        filters = {
            "user_id": user_id,
            "is_archived": False,
        }
        sessions = (
            await self.collection.find(filters).sort("updated_at", -1).skip(skip).limit(limit).to_list(None)
        )
        total = await self.collection.count_documents(filters)
        return sessions, total

    async def update(
        self,
        session_id: str,
        user_id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any] | None:
        session = await self.get(session_id, user_id)
        if session is None:
            return None

        update_data: dict[str, Any] = {
            "updated_at": datetime.now(UTC),
        }
        if title is not None:
            update_data["title"] = title.strip()
        if description is not None:
            update_data["description"] = self._normalize_description(description)

        await self.collection.update_one({"_id": session["_id"]}, {"$set": update_data})
        return {
            **session,
            **update_data,
        }

    async def delete(self, session_id: str, user_id: str) -> bool:
        session = await self.get(session_id, user_id)
        if session is None:
            return False

        result = await self.collection.update_one(
            {"_id": session["_id"]},
            {
                "$set": {
                    "is_archived": True,
                    "updated_at": datetime.now(UTC),
                }
            },
        )
        return result.modified_count > 0

    @staticmethod
    def _normalize_description(description: str | None) -> str | None:
        if description is None:
            return None

        cleaned = description.strip()
        return cleaned or None

    @staticmethod
    def _to_object_id(value: str) -> ObjectId | None:
        if not ObjectId.is_valid(value):
            return None
        return ObjectId(value)
