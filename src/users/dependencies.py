from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.users.repository import UserRepository
from src.users.service import UserService


def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    repository = UserRepository(session)

    return UserService(repository)