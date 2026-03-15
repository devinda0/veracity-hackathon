from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def auth_status() -> dict[str, str]:
    return {"status": "ok", "service": "auth"}

