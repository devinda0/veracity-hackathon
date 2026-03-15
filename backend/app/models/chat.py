from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

