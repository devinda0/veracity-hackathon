from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BusinessContextDoc(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    session_id: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
