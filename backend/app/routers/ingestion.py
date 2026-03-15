from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, HttpUrl

from app.core.logger import get_logger
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.services.url_ingestion import URLIngestionError, URLIngestionService

logger = get_logger(__name__)
router = APIRouter()


class URLIngestionRequest(BaseModel):
    url: HttpUrl
    session_id: str = Field(min_length=1, max_length=255)


@router.post("/ingest-url", status_code=status.HTTP_201_CREATED)
async def ingest_url(
    request: URLIngestionRequest,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict[str, str | int | bool]:
    service = URLIngestionService(db)

    try:
        result = await service.ingest_url(str(request.url), request.session_id, current_user.id)
        existing_context = await db.business_context.find_one(
            {
                "user_id": current_user.id,
                "session_id": request.session_id,
                "source_type": "url",
                "url_hash": result["url_hash"],
            }
        )

        if existing_context is None:
            context_doc = {
                "user_id": current_user.id,
                "session_id": request.session_id,
                "source_type": "url",
                "url": result["url"],
                "url_hash": result["url_hash"],
                "content": result["content"],
                "chunks": result["chunks"],
                "metadata": {
                    "method": result["method"],
                    "cached": result["cached"],
                },
                "created_at": datetime.now(UTC),
            }
            context_result = await db.business_context.insert_one(context_doc)
            context_id = str(context_result.inserted_id)
        else:
            context_id = str(existing_context["_id"])
            logger.info(
                "url_ingestion_deduplicated",
                url=result["url"],
                session_id=request.session_id,
                user_id=current_user.id,
                context_id=context_id,
            )

        await db.url_ingestions.update_one(
            {
                "user_id": current_user.id,
                "session_id": request.session_id,
                "url_hash": result["url_hash"],
            },
            {
                "$set": {
                    "user_id": current_user.id,
                    "session_id": request.session_id,
                    "url": result["url"],
                    "url_hash": result["url_hash"],
                    "chunk_count": len(result["chunks"]),
                    "source": result["source"],
                    "method": result["method"],
                    "updated_at": datetime.now(UTC),
                },
                "$setOnInsert": {
                    "created_at": datetime.now(UTC),
                },
            },
            upsert=True,
        )

        return {
            "context_id": context_id,
            "url": result["url"],
            "chunks": len(result["chunks"]),
            "source": result["source"],
            "deduplicated": existing_context is not None,
        }
    except URLIngestionError as exc:
        logger.warning("url_ingestion_rejected", url=str(request.url), error=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("url_ingestion_failed", url=str(request.url), error=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="URL ingestion failed") from exc
