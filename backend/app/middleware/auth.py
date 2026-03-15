from typing import Annotated

from bson import ObjectId
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import AuthException
from app.core.logger import get_logger
from app.core.security import decode_access_token
from app.db.mongo import get_mongo_db
from app.models.auth import AuthenticatedUser

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)],
) -> AuthenticatedUser:
    if credentials is None or not credentials.credentials:
        raise AuthException("Missing authentication credentials")

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not ObjectId.is_valid(user_id):
        raise AuthException("Invalid token")

    user = await db.users.find_one({"_id": ObjectId(user_id), "is_active": True})
    if user is None:
        logger.warning("auth_user_lookup_failed", user_id=user_id)
        raise AuthException("Invalid token")

    return AuthenticatedUser(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
    )
