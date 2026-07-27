import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.masters.models import Master
from src.masters.repository import MasterRepository


@pytest.fixture
def master_repository(
    db_session: AsyncSession,
) -> MasterRepository:
    return MasterRepository(db_session)


@pytest.fixture
async def create_master(
    db_session: AsyncSession,
) -> Master:
    master = Master(
        first_name="Kirill",
        last_name="Test",
        description="Backend developer",
        experience=3,
        education="IT",
    )

    db_session.add(master)

    await db_session.commit()
    await db_session.refresh(master)

    return master