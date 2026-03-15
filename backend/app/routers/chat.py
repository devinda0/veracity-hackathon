from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def chat_status() -> dict[str, str]:
    return {"status": "ok", "service": "chat"}

