from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    STATUS = "status"
    ARTIFACT = "artifact"
    THINKING = "thinking"
    FINAL = "final"
    ERROR = "error"


class WSMessage(BaseModel):
    type: MessageType
    session_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    content: str
    agent: str | None = None
    metadata: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


def build_message(
    message_type: MessageType,
    session_id: str,
    content: str,
    *,
    agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return WSMessage(
        type=message_type,
        session_id=session_id,
        content=content,
        agent=agent,
        metadata=metadata,
    ).to_payload()


def status_message(
    session_id: str,
    agent: str,
    status: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_message(MessageType.STATUS, session_id, status, agent=agent, metadata=metadata)


def artifact_message(
    session_id: str,
    artifact_type: str,
    data: dict[str, Any],
    *,
    agent: str | None = None,
) -> dict[str, Any]:
    return build_message(
        MessageType.ARTIFACT,
        session_id,
        artifact_type,
        agent=agent,
        metadata=data,
    )


def thinking_message(session_id: str, agent: str, reasoning: str) -> dict[str, Any]:
    return build_message(MessageType.THINKING, session_id, reasoning, agent=agent)


def final_message(
    session_id: str,
    content: str,
    *,
    agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return build_message(
        MessageType.FINAL,
        session_id,
        content,
        agent=agent,
        metadata=metadata,
    )


def error_message(session_id: str, error: str, *, agent: str | None = None) -> dict[str, Any]:
    return build_message(MessageType.ERROR, session_id, error, agent=agent)
