from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import NotFoundException
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.models.session import (
    ChatMessageResponse,
    SessionDetailResponse,
    SessionListResponse,
    SessionResponse,
)
from app.services.session import SessionService

router = APIRouter()

DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)]
CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


class CreateSessionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("Title is required")
        return title

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class UpdateSessionRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        title = value.strip()
        if not title:
            raise ValueError("Title is required")
        return title

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


@router.get("/status")
async def sessions_status() -> dict[str, str]:
    return {"status": "ok", "service": "sessions"}


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    db: DatabaseDep,
    current_user: CurrentUserDep,
) -> SessionResponse:
    session = await SessionService(db).create(current_user.id, request.title, request.description)
    return _serialize_session(session)


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    db: DatabaseDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
) -> SessionListResponse:
    sessions, total = await SessionService(db).list_user_sessions(current_user.id, skip, limit)
    return SessionListResponse(
        sessions=[_serialize_session(session) for session in sessions],
        total=total,
    )


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: str,
    db: DatabaseDep,
    current_user: CurrentUserDep,
) -> SessionDetailResponse:
    session, messages = await SessionService(db).get_with_history(session_id, current_user.id)
    if session is None:
        raise NotFoundException("Session not found")

    return SessionDetailResponse(
        **_serialize_session_payload(session),
        messages=[_serialize_message(message) for message in messages],
    )


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    db: DatabaseDep,
    current_user: CurrentUserDep,
) -> SessionResponse:
    service = SessionService(db)
    if request.title is None and request.description is None:
        session = await service.get(session_id, current_user.id)
    else:
        session = await service.update(
            session_id,
            current_user.id,
            title=request.title,
            description=request.description,
        )

    if session is None:
        raise NotFoundException("Session not found")

    return _serialize_session(session)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: DatabaseDep,
    current_user: CurrentUserDep,
) -> Response:
    deleted = await SessionService(db).delete(session_id, current_user.id)
    if not deleted:
        raise NotFoundException("Session not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _serialize_session(session: dict[str, Any]) -> SessionResponse:
    return SessionResponse(**_serialize_session_payload(session))


def _serialize_session_payload(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(session["_id"]),
        "title": session["title"],
        "description": session.get("description"),
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
        "message_count": session.get("message_count", 0),
    }


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
