from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.users.models import User
from src.users.schemas import UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_my_profile(
    current_user: User = Depends(
        get_current_user
    ),
):
    return current_user