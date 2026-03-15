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
    """Standard envelope for inter-agent communication."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str
    recipient: str
    message_type: MessageType
    payload: dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
