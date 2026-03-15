from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SessionDoc(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    user_id: str
    title: str
    description: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_archived: bool = False
    message_count: int = 0


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    artifacts: list[dict[str, Any]] | None = None
    agent_trace: dict[str, Any] | None = None
    timestamp: datetime
    tokens_used: int | None = None
    cost: float | None = None


class SessionResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class SessionDetailResponse(SessionResponse):
    messages: list[ChatMessageResponse] = Field(default_factory=list)


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int
