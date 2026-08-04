from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.masters.repository import MasterRepository
from src.masters.service import MasterService


def get_master_service(
    session: AsyncSession = Depends(get_async_session)
) -> MasterService:

    repository = MasterRepository(session)


    return MasterService(repository)