from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Session(BaseModel):
    id: str
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    archived: bool = False

