from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated, Any

from bson import ObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import NotFoundException
from app.core.logger import get_logger
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.models.session import ChatMessageResponse
from app.services.orchestrator import OrchestratorService
from app.services.session import SessionService

router = APIRouter()
logger = get_logger(__name__)

DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)]
CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


class ChatMessageRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=255)
    query: str = Field(min_length=1, max_length=10000)
    business_context: str | None = Field(default=None, max_length=20000)

    @field_validator("session_id", "query")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field is required")
        return cleaned

    @field_validator("business_context")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ChatMessageQueuedResponse(BaseModel):
    message_id: str
    session_id: str
    status: str = "queued"


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[ChatMessageResponse]
    total: int


@router.get("/status")
async def chat_status() -> dict[str, str]:
    return {"status": "ok", "service": "chat"}


@router.post("/messages", response_model=ChatMessageQueuedResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_message(
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseDep,
    current_user: CurrentUserDep,
) -> ChatMessageQueuedResponse:
    session = await SessionService(db).get(request.session_id, current_user.id)
    if session is None:
        raise NotFoundException("Session not found")

    message_id = str(uuid.uuid4())
    timestamp = datetime.now(UTC)
    user_message = {
        "_id": ObjectId(),
        "message_id": message_id,
        "session_id": request.session_id,
        "user_id": current_user.id,
        "role": "user",
        "content": request.query,
        "timestamp": timestamp,
    }

    try:
        await db.chat_history.insert_one(user_message)
        await db.sessions.update_one(
            {"_id": session["_id"]},
            {
                "$set": {"updated_at": timestamp},
                "$inc": {"message_count": 1},
            },
        )
    except Exception as exc:
        logger.error("chat_message_store_failed", session_id=request.session_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store chat message",
        ) from exc

    background_tasks.add_task(
        _run_orchestrator,
        db,
        request.session_id,
        current_user.id,
        request.query,
        request.business_context,
        message_id,
    )

    return ChatMessageQueuedResponse(
        message_id=message_id,
        session_id=request.session_id,
    )


@router.get("/messages/{session_id}", response_model=ChatHistoryResponse)
async def get_messages(
    session_id: str,
    db: DatabaseDep,
    current_user: CurrentUserDep,
) -> ChatHistoryResponse:
    session = await SessionService(db).get(session_id, current_user.id)
    if session is None:
        raise NotFoundException("Session not found")

    messages = await db.chat_history.find({"session_id": session_id}).sort("timestamp", 1).to_list(None)
    serialized_messages = [_serialize_message(message) for message in messages]
    return ChatHistoryResponse(
        session_id=session_id,
        messages=serialized_messages,
        total=len(serialized_messages),
    )


async def _run_orchestrator(
    db: AsyncIOMotorDatabase,
    session_id: str,
    user_id: str,
    query: str,
    business_context: str | None,
    message_id: str,
) -> None:
    try:
        service = OrchestratorService(db)
        await service.run(
            session_id=session_id,
            user_id=user_id,
            query=query,
            business_context=business_context,
        )
    except Exception as exc:
        logger.error(
            "chat_orchestrator_failed",
            message_id=message_id,
            session_id=session_id,
            error=str(exc),
        )


def _serialize_message(message: dict[str, Any]) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=str(message["_id"]),
        role=message["role"],
        content=message["content"],
        artifacts=message.get("artifacts"),
        agent_trace=message.get("agent_trace"),
        timestamp=message["timestamp"],
        tokens_used=message.get("tokens_used"),
        cost=message.get("cost"),
    )
