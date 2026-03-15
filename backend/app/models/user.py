from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class UserDoc(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    email: str
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
