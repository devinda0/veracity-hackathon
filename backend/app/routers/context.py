from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.logger import get_logger
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.services.document_parser import DocumentParseError, DocumentParser
from app.services.embedding import EmbeddingService
from app.services.session import SessionService
from app.services.url_ingestion import URLIngestionError, URLIngestionService

logger = get_logger(__name__)
router = APIRouter()

ALLOWED_DOCUMENT_TYPES = {"pdf", "docx", "txt"}
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
BUSINESS_CONTEXT_COLLECTION = "business_context"


class TextContextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    title: str | None = Field(default=None, max_length=255)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("text cannot be blank")
        return normalized

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class URLContextRequest(BaseModel):
    url: HttpUrl


@router.post("/{session_id}/context", status_code=status.HTTP_201_CREATED)
async def upload_context(
    session_id: str,
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict[str, Any]:
    await _ensure_session_access(session_id, db, current_user.id)

    filename = file.filename or ""
    file_ext = Path(filename).suffix.lower().lstrip(".")
    temp_path: str | None = None

    if not filename or file_ext not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type must be one of: {sorted(ALLOWED_DOCUMENT_TYPES)}",
        )

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
        if len(contents) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="File too large. Max 10MB.",
            )

        with NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_file:
            temp_file.write(contents)
            temp_file.flush()
            temp_path = temp_file.name

        parsed = DocumentParser.parse_file(temp_path, file_ext)
        chunks = parsed["chunks"]
        if not chunks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No readable content found in file")

        metadata = dict(parsed["metadata"])
        if file_ext == "txt" or not metadata.get("title"):
            metadata["title"] = Path(filename).stem

        created_at = datetime.now(UTC)
        embedding_service = EmbeddingService(db=db)
        indexed_chunks = await embedding_service.index_chunks(
            chunks,
            session_id,
            f"document:{filename}",
            metadata={
                "source_type": "document",
                "title": metadata.get("title"),
                "file_type": file_ext,
            },
            created_at=created_at,
        )

        document = {
            "user_id": current_user.id,
            "session_id": session_id,
            "source_type": "document",
            "source": filename,
            "filename": filename,
            "file_type": file_ext,
            "title": metadata.get("title"),
            "content": parsed["content"],
            "chunks": chunks,
            "chunk_count": len(chunks),
            "metadata": metadata,
            "created_at": created_at,
        }

        result = await db.business_context.insert_one(document)
        context_id = str(result.inserted_id)

        logger.info(
            "session_context_document_uploaded",
            context_id=context_id,
            filename=filename,
            session_id=session_id,
            user_id=current_user.id,
            chunks=len(chunks),
        )
        return {
            "context_id": context_id,
            "type": "document",
            "source": filename,
            "chunk_count": len(chunks),
            "metadata": metadata,
            "embedding": _embedding_stats(indexed_chunks),
        }
    except HTTPException:
        raise
    except DocumentParseError as exc:
        logger.warning("session_context_document_rejected", filename=filename, session_id=session_id, error=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("session_context_document_failed", filename=filename, session_id=session_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Context upload failed",
        ) from exc
    finally:
        await file.close()
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


@router.post("/{session_id}/context/url", status_code=status.HTTP_201_CREATED)
async def ingest_context_url(
    session_id: str,
    request: URLContextRequest,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict[str, Any]:
    await _ensure_session_access(session_id, db, current_user.id)

    url_service = URLIngestionService(db)

    try:
        result = await url_service.ingest_url(str(request.url), session_id, current_user.id)
        created_at = datetime.now(UTC)
        embedding_service = EmbeddingService(db=db)
        indexed_chunks = await embedding_service.index_chunks(
            result["chunks"],
            session_id,
            f"url:{result['url']}",
            metadata={
                "source_type": "url",
                "url_hash": result["url_hash"],
                "method": result["method"],
                "cached": result["cached"],
                "source": result["source"],
            },
            created_at=created_at,
        )

        existing_context = await db.business_context.find_one(
            {
                "user_id": current_user.id,
                "session_id": session_id,
                "source_type": "url",
                "url_hash": result["url_hash"],
            }
        )

        if existing_context is None:
            context_doc = {
                "user_id": current_user.id,
                "session_id": session_id,
                "source_type": "url",
                "source": result["url"],
                "title": result["url"],
                "url": result["url"],
                "url_hash": result["url_hash"],
                "content": result["content"],
                "chunks": result["chunks"],
                "chunk_count": len(result["chunks"]),
                "metadata": {
                    "method": result["method"],
                    "cached": result["cached"],
                    "source": result["source"],
                },
                "created_at": created_at,
            }
            context_result = await db.business_context.insert_one(context_doc)
            context_id = str(context_result.inserted_id)
            deduplicated = False
        else:
            context_id = str(existing_context["_id"])
            deduplicated = True

        await db.url_ingestions.update_one(
            {
                "user_id": current_user.id,
                "session_id": session_id,
                "url_hash": result["url_hash"],
            },
            {
                "$set": {
                    "user_id": current_user.id,
                    "session_id": session_id,
                    "url": result["url"],
                    "url_hash": result["url_hash"],
                    "chunk_count": len(result["chunks"]),
                    "source": result["source"],
                    "method": result["method"],
                    "updated_at": created_at,
                },
                "$setOnInsert": {
                    "created_at": created_at,
                },
            },
            upsert=True,
        )

        logger.info(
            "session_context_url_ingested",
            context_id=context_id,
            url=result["url"],
            session_id=session_id,
            user_id=current_user.id,
            chunks=len(result["chunks"]),
            deduplicated=deduplicated,
        )
        return {
            "context_id": context_id,
            "type": "url",
            "source": result["url"],
            "chunk_count": len(result["chunks"]),
            "metadata": {
                "method": result["method"],
                "cached": result["cached"],
                "source": result["source"],
                "deduplicated": deduplicated,
            },
            "embedding": _embedding_stats(indexed_chunks),
        }
    except URLIngestionError as exc:
        logger.warning("session_context_url_rejected", url=str(request.url), session_id=session_id, error=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("session_context_url_failed", url=str(request.url), session_id=session_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="URL context ingestion failed",
        ) from exc


@router.post("/{session_id}/context/text", status_code=status.HTTP_201_CREATED)
async def add_text_context(
    session_id: str,
    request: TextContextRequest,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict[str, Any]:
    await _ensure_session_access(session_id, db, current_user.id)

    try:
        chunks = DocumentParser.chunk_text(request.text)
        if not chunks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text context is empty")

        source = request.title or "Text snippet"
        created_at = datetime.now(UTC)
        embedding_service = EmbeddingService(db=db)
        indexed_chunks = await embedding_service.index_chunks(
            chunks,
            session_id,
            f"text:{source}",
            metadata={
                "source_type": "text",
                "title": source,
                "characters": len(request.text),
            },
            created_at=created_at,
        )

        context_doc = {
            "user_id": current_user.id,
            "session_id": session_id,
            "source_type": "text",
            "source": source,
            "title": source,
            "content": request.text,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "metadata": {
                "characters": len(request.text),
            },
            "created_at": created_at,
        }

        result = await db.business_context.insert_one(context_doc)
        context_id = str(result.inserted_id)

        logger.info(
            "session_context_text_added",
            context_id=context_id,
            session_id=session_id,
            user_id=current_user.id,
            chunks=len(chunks),
        )
        return {
            "context_id": context_id,
            "type": "text",
            "source": source,
            "chunk_count": len(chunks),
            "metadata": {
                "characters": len(request.text),
            },
            "embedding": _embedding_stats(indexed_chunks),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("session_context_text_failed", session_id=session_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Text context ingestion failed",
        ) from exc


@router.get("/{session_id}/context")
async def get_session_context(
    session_id: str,
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict[str, Any]:
    await _ensure_session_access(session_id, db, current_user.id)

    contexts = (
        await db.business_context.find(
            {
                "session_id": session_id,
                "user_id": current_user.id,
            }
        )
        .sort("created_at", -1)
        .to_list(None)
    )

    serialized_contexts = [_serialize_context(context) for context in contexts]

    return {
        "session_id": session_id,
        "contexts": serialized_contexts,
        "total": len(serialized_contexts),
        "total_chunks": sum(context["chunk_count"] for context in serialized_contexts),
    }


async def _ensure_session_access(session_id: str, db: AsyncIOMotorDatabase, user_id: str) -> None:
    session = await SessionService(db).get(session_id, user_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")


def _embedding_stats(indexed_chunks: int) -> dict[str, Any]:
    return {
        "model": EmbeddingService.EMBEDDING_MODEL,
        "dimensions": EmbeddingService.EMBEDDING_DIM,
        "indexed_chunks": indexed_chunks,
        "collection": BUSINESS_CONTEXT_COLLECTION,
    }


def _serialize_context(context: dict[str, Any]) -> dict[str, Any]:
    created_at = context.get("created_at")
    return {
        "context_id": str(context["_id"]),
        "type": context.get("source_type", "unknown"),
        "source": context.get("source") or context.get("title") or "Untitled context",
        "chunk_count": context.get("chunk_count", len(context.get("chunks", []))),
        "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else None,
        "metadata": dict(context.get("metadata", {})),
    }
