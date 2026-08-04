import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.masters.models import Master
from src.masters.repository import MasterRepository


@pytest.mark.anyio
async def test_get_all_empty(
    master_repository: MasterRepository,
):

    masters = await master_repository.get_all()

    assert masters == []
    

@pytest.mark.anyio
async def test_get_all_with_master(
    create_master,
    master_repository: MasterRepository,
    
):
    masters = await master_repository.get_all()

    assert len(masters) == 1

    master = masters[0]

    assert master.id == create_master.id
    assert master.first_name == create_master.first_name


@pytest.mark.anyio
async def test_get_by_id_master(
    create_master,
    master_repository: MasterRepository,
    
):

    master = await master_repository.get_by_id(create_master.id)

    assert "id" != None

    assert master.id == create_master.id


@pytest.mark.anyio
async def test_get_by_id_master_None(
    master_repository: MasterRepository,
    
):
    fake_uuid = uuid.uuid4()
    master = await master_repository.get_by_id(fake_uuid)


    assert master is None


@pytest.mark.anyio
async def test_create_master(
    db_session: AsyncSession,
    master_repository: MasterRepository,
    
): 

    master_create = Master(
        first_name="Artem",
        last_name="Test",
        description="Backend developer",
        experience=2,
        education="IT"
    )  


    master = await master_repository.create(master_create)


    master_database = await db_session.get(
        Master,
        master.id
    )

    assert master.id is not None
    assert master.last_name == "Test"

    assert master_database.id is not None
    assert master_database.id == master.id


@pytest.mark.anyio
async def test_update(
    master_repository: MasterRepository,
    create_master: Master
):
    create_master.first_name = "Fedor"
    create_master.experience = 10


    master = await master_repository.update(
        create_master
    )


    assert master.id == create_master.id
    assert master.experience == 10


@pytest.mark.anyio
async def test_delete(
    master_repository: MasterRepository,
    create_master: Master
):

    master_id = create_master.id

    await master_repository.delete(create_master)

    master_get_by_id = await master_repository.get_by_id(master_id)

    assert master_get_by_id is None

