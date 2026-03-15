from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, model_validator

from app.core.logger import get_logger
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.services.embedding import EmbeddingService

logger = get_logger(__name__)
router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    session_id: str = Field(min_length=1, max_length=255)
    limit: int = Field(default=5, ge=1, le=20)
    source: str | None = Field(default=None, min_length=1, max_length=1024)
    created_after: datetime | None = None
    created_before: datetime | None = None

    @model_validator(mode="after")
    def validate_date_window(self) -> "SearchRequest":
        if self.created_after and self.created_before and self.created_after > self.created_before:
            raise ValueError("created_after must be earlier than created_before")
        return self


@router.post("/semantic-search")
async def semantic_search(
    request: SearchRequest,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict[str, object]:
    service = EmbeddingService(db=db)

    try:
        results = await service.search(
            query=request.query,
            session_id=request.session_id,
            limit=request.limit,
            source=request.source,
            created_after=request.created_after,
            created_before=request.created_before,
        )
    except ValueError as exc:
        logger.warning(
            "semantic_search_rejected",
            session_id=request.session_id,
            user_id=current_user.id,
            error=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception(
            "semantic_search_failed",
            session_id=request.session_id,
            user_id=current_user.id,
            error=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Semantic search failed") from exc

    return {
        "query": request.query,
        "session_id": request.session_id,
        "results": results,
        "total": len(results),
    }
