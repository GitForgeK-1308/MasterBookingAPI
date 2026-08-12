from fastapi.security import OAuth2PasswordRequestForm

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from src.auth.dependencies import get_current_user
from src.auth.token import create_access_token
from src.users.dependencies import get_user_avatar_service, get_user_service
from src.users.exceptions import (
    AvatarTooLargeError,
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidAvatarTypeError,
    InvalidCredentialsError,
)

from src.users.models import User
from src.users.schemas import UserAvatarResponse, UserProfileUpdate, UserRegister, UserResponse, TokenResponse
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


@router.patch(
    "/users/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    service: UserService = Depends(
        get_user_service
    ),
):
    return await service.update_profile(
        user=current_user,
        data=data,
    )



@router.post(
    "/users/me/avatar",
    response_model=UserAvatarResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_my_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    ),
    service: UserService = Depends(
        get_user_avatar_service
    ),
):
    try:
        user = await service.upload_avatar(
            user=current_user,
            file=file,
        )

        return UserAvatarResponse(
            avatar_url=service.get_avatar_url(
                user.avatar_storage_key
            )
        )

    except AvatarTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Файл слишком большой. Максимальный размер — 5 МБ.",
        )

    except InvalidAvatarTypeError:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Разрешены только JPEG, PNG и WEBP.",
        )