from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import AuthException

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def access_token_expires_in_seconds() -> int:
    return settings.JWT_EXPIRATION_HOURS * 3600


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(hours=settings.JWT_EXPIRATION_HOURS))
    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": now})

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthException("Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthException("Invalid token") from exc

    if not isinstance(payload, dict):
        raise AuthException("Invalid token")

    return payload
