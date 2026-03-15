"""A2A protocol primitives used by agent-to-agent communication."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Supported high-level message kinds between agents."""

    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"


class A2AMessage(BaseModel):
    """Inter-agent communication envelope for A2A transport."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str
    recipient: str
    message_type: MessageType
    payload: dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> dict[str, Any]:
        """Serialize message to a JSON-compatible dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2AMessage":
        """Create message instance from a dictionary payload."""
        return cls(**data)

    def to_json(self) -> str:
        """Serialize message to JSON text."""
        return self.model_dump_json()

    @classmethod
    def from_json(cls, raw: str) -> "A2AMessage":
        """Create message instance from JSON text."""
        return cls.model_validate_json(raw)
