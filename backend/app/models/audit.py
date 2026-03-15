from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogDoc(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    user_id: str
    action: str
    resource: str | None = None
    status: str
    details: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

