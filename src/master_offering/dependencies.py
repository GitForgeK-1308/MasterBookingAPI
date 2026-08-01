from fastapi import Depends
from src.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.master_offering.repository import MasterOfferingRepository
from src.master_offering.service import MasterOfferingService


def get_offering_service(
    session: AsyncSession = Depends(get_async_session)
) -> MasterOfferingService:

    repository = MasterOfferingRepository(session)


    return MasterOfferingService(repository)
