from fastapi.security import OAuth2PasswordRequestForm

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from src.auth.token import create_access_token
from src.users.dependencies import get_user_service
from src.users.exceptions import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
)

from src.users.schemas import UserRegister, UserResponse, TokenResponse
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


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service),
):
    try:
        user = await service.authenticate_user(
            email=form_data.username,
            password=form_data.password,
        )

        access_token = create_access_token(
            user_id=user.id
        )

        return TokenResponse(
            access_token=access_token
        )

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль!",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт пользователя отключён!",
        )