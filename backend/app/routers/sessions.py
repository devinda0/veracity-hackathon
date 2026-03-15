from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def sessions_status() -> dict[str, str]:
    return {"status": "ok", "service": "sessions"}

