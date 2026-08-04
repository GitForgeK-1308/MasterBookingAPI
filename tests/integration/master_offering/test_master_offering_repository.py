import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from src.master_offering.models import MasterOffering
from src.master_offering.repository import MasterOfferingRepository
from src.masters.models import Master

    

@pytest.mark.anyio
async def test_get_offering_by_id(
    create_offering: MasterOffering,
    offering_repository: MasterOfferingRepository,
    
):

    offering = await offering_repository.get_by_id(create_offering.id)


    assert offering is not None
    assert offering.id == create_offering.id
    assert offering.master_id == create_offering.master_id
    


@pytest.mark.anyio
async def test_get_by_id_master_None(
    master_repository: MasterOfferingRepository,
    
):
    fake_uuid = uuid.uuid4()
    master = await master_repository.get_by_id(fake_uuid)


    assert master is None


@pytest.mark.anyio
async def test_create_offering(
    create_master: Master,
    db_session: AsyncSession,
    offering_repository: MasterOfferingRepository,
):
    offering_create = MasterOffering(
        master_id=create_master.id,
        title="Стрижка для волос",
        description="ВЦВЦВ",
        price=Decimal("113.00"),
        duration_minutes=100,
    )

    offering = await offering_repository.create(
        offering_create
    )

    offering_from_database = await db_session.get(
        MasterOffering,
        offering.id,
    )

    assert offering.id is not None
    assert offering.master_id == create_master.id
    assert offering.title == "Стрижка для волос"
    assert offering.description == "ВЦВЦВ"
    assert offering.price == Decimal("113.00")
    assert offering.duration_minutes == 100

    assert offering_from_database is not None
    assert offering_from_database.id == offering.id


@pytest.mark.anyio
async def test_update(
    offering_repository: MasterOfferingRepository,
    create_master: MasterOffering
):
    create_master.title = "Fedor"
    create_master.description = "ОВЦЛВЦВ"


    offering = await offering_repository.update(
        create_master
    )


    assert offering.id == create_master.id
    assert offering.title == "Fedor"


@pytest.mark.anyio
async def test_delete(
    offering_repository: MasterOfferingRepository,
    create_master: MasterOffering
):

    master_id = create_master.id

    await offering_repository.delete(create_master)

    master_get_by_id = await offering_repository.get_by_id(master_id)

    assert master_get_by_id is None

