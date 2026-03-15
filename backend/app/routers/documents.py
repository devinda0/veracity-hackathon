from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logger import get_logger
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser
from app.services.document_parser import DocumentParseError, DocumentParser

logger = get_logger(__name__)
router = APIRouter()

ALLOWED_DOCUMENT_TYPES = {"pdf", "docx", "txt"}


@router.post("/upload-document", status_code=status.HTTP_201_CREATED)
async def upload_document(
    session_id: str,
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> dict[str, str | int | dict]:
    filename = file.filename or ""
    file_ext = Path(filename).suffix.lower().lstrip(".")

    if not filename or file_ext not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type must be one of: {sorted(ALLOWED_DOCUMENT_TYPES)}",
        )

    temp_path: str | None = None
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

        with NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_file:
            temp_file.write(contents)
            temp_file.flush()
            temp_path = temp_file.name

        parsed = DocumentParser.parse_file(temp_path, file_ext)
        metadata = dict(parsed["metadata"])
        if file_ext == "txt" or not metadata.get("title"):
            metadata["title"] = Path(filename).stem

        title = metadata["title"]
        document = {
            "user_id": current_user.id,
            "session_id": session_id,
            "source_type": "document",
            "filename": filename,
            "file_type": file_ext,
            "title": title,
            "content": parsed["content"],
            "chunks": parsed["chunks"],
            "metadata": metadata,
            "created_at": datetime.now(UTC),
        }

        result = await db.business_context.insert_one(document)
        logger.info(
            "document_uploaded",
            document_id=str(result.inserted_id),
            filename=filename,
            session_id=session_id,
            user_id=current_user.id,
            chunks=len(parsed["chunks"]),
        )
        return {
            "document_id": str(result.inserted_id),
            "filename": filename,
            "chunks": len(parsed["chunks"]),
            "metadata": metadata,
        }
    except HTTPException:
        raise
    except DocumentParseError as exc:
        logger.warning("document_upload_rejected", filename=filename, session_id=session_id, error=str(exc))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("document_upload_failed", filename=filename, session_id=session_id, error=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Document upload failed") from exc
    finally:
        await file.close()
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)
