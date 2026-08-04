import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.master_offering.models import MasterOffering
from src.masters.models import Master
from src.master_offering.repository import MasterOfferingRepository


@pytest.fixture
def offering_repository(
    db_session: AsyncSession,
) -> MasterOfferingRepository:
    return MasterOfferingRepository(db_session)


@pytest.fixture
async def create_offering(
    db_session: AsyncSession,
    create_master: Master,
):
    offering = MasterOffering(
        master_id=create_master.id,
        title="Стрижка",
        description="Описание",
        price=1500,
        duration_minutes=60,
    )

    db_session.add(offering)
    await db_session.commit()
    await db_session.refresh(offering)

    return offering