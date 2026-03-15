from typing import Annotated

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.auth import AuthenticatedUser, UserResponse

router = APIRouter()

CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


@router.get("/me", response_model=UserResponse)
async def get_authenticated_user(current_user: CurrentUserDep) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
    )
