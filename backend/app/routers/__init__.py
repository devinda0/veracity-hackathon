from fastapi import APIRouter

from app.core.config import get_settings
from app.routers import auth, chat, documents, health, protected, sessions, websocket

settings = get_settings()

api_router = APIRouter(prefix=settings.API_PREFIX)
api_v1_router = APIRouter(prefix=f"/{settings.API_VERSION}")

api_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_v1_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_v1_router.include_router(protected.router, prefix="/protected", tags=["protected"])
api_v1_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_v1_router.include_router(websocket.router, tags=["ws"])
api_router.include_router(api_v1_router)
