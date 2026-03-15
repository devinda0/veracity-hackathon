from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import APIException, AuthException
from app.core.logger import get_logger
from app.core.security import (
    access_token_expires_in_seconds,
    create_access_token,
    hash_password,
    normalize_email,
    verify_password,
)
from app.db.mongo import get_mongo_db
from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser, LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()
logger = get_logger(__name__)

DatabaseDep = Annotated[AsyncIOMotorDatabase, Depends(get_mongo_db)]
CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


@router.get("/status")
async def auth_status() -> dict[str, str]:
    return {"status": "ok", "service": "auth"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: DatabaseDep) -> UserResponse:
    email = normalize_email(str(request.email))
    existing_user = await db.users.find_one({"email": email})
    if existing_user is not None:
        raise APIException(
            detail="User already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_EXISTS",
        )

    now = datetime.now(UTC)
    user_doc = {
        "email": email,
        "password_hash": hash_password(request.password),
        "name": request.name,
        "created_at": now,
        "updated_at": now,
        "is_active": True,
    }

    try:
        result = await db.users.insert_one(user_doc)
    except DuplicateKeyError as exc:
        raise APIException(
            detail="User already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_EXISTS",
        ) from exc

    logger.info("user_registered", user_id=str(result.inserted_id), email=email)
    return UserResponse(id=str(result.inserted_id), email=email, name=request.name)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DatabaseDep) -> TokenResponse:
    email = normalize_email(str(request.email))
    user = await db.users.find_one({"email": email})
    if user is None or not user.get("is_active", True):
        logger.warning("login_failed", email=email, reason="user_not_found")
        raise AuthException("Invalid credentials")

    password_hash = user.get("password_hash")
    if not isinstance(password_hash, str) or not verify_password(request.password, password_hash):
        logger.warning("login_failed", email=email, reason="invalid_password")
        raise AuthException("Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"]},
    )
    logger.info("user_login_success", user_id=str(user["_id"]), email=email)

    return TokenResponse(
        access_token=access_token,
        expires_in=access_token_expires_in_seconds(),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(current_user: CurrentUserDep) -> TokenResponse:
    access_token = create_access_token(
        data={"sub": current_user.id, "email": str(current_user.email)},
    )
    return TokenResponse(
        access_token=access_token,
        expires_in=access_token_expires_in_seconds(),
    )
