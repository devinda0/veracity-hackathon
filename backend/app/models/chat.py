from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageDoc(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    session_id: str
    role: str
    content: str
    artifacts: list[dict[str, Any]] | None = None
    agent_trace: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tokens_used: int | None = None
    cost: float | None = None
