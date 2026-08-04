from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session
from src.master_schedule.repository import MasterScheduleRepository
from src.master_schedule.service import MasterScheduleService


def get_schedule_service(
    session: AsyncSession = Depends(get_async_session)
) -> MasterScheduleService:

    repository = MasterScheduleRepository(session)


    return MasterScheduleService(repository)
