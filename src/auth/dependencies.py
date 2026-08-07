from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from src.auth.token import decode_access_token
from src.users.exceptions import UserNotFoundError
from src.users.models import User, UserRole
from src.users.service import UserService
from src.users.dependencies import get_user_service


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить пользователя!",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        user_id = decode_access_token(token)

    except InvalidTokenError:
        raise credentials_exception

    try:
        user = await service.get_user_by_id(
            user_id
        )

    except UserNotFoundError:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт пользователя отключён!",
        )

    return user


async def get_current_client(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только клиентам!",
        )

    return current_user


async def get_current_master_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.MASTER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только мастерам!",
        )

    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только администраторам!",
        )

    return current_user