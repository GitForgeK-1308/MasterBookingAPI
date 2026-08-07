from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.masters.repository import MasterRepository
from src.masters.service import MasterService
from src.users.repository import UserRepository


def get_master_service(
    session: AsyncSession = Depends(get_async_session)
) -> MasterService:

    master_repository = MasterRepository(session)
    user_repository = UserRepository(session)

    return MasterService(
        repository=master_repository,
        user_repository=user_repository,
    )