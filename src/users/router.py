from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.users.dependencies import get_user_service
from src.users.exceptions import EmailAlreadyExistsError
from src.users.schemas import UserRegister, UserResponse
from src.users.service import UserService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: UserRegister,
    service: UserService = Depends(get_user_service),
):
    try:
        return await service.register_user(data)

    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует!",
        )