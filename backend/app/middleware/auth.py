from fastapi import Header

from app.core.exceptions import AuthException


async def require_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthException()
    return authorization.removeprefix("Bearer ").strip()

