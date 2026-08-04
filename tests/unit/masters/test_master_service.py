import uuid
from unittest.mock import AsyncMock

import pytest

from src.masters.models import Master
from src.masters.repository import MasterRepository
from src.masters.schemas import MasterUpdate
from src.masters.service import MasterService


@pytest.mark.anyio
async def test_get_all_masters():

    repository = AsyncMock()

    masters = [
    Master(
        first_name="Kirill",
        last_name="Test",
        description="Backend",
        experience=3,
        education="IT"
    )
]   

    repository.get_all.return_value = masters


    service = MasterService(
        repository
    )


    result = await service.get_masters()


    assert result == masters


    repository.get_all.assert_called_once()


@pytest.mark.anyio
async def test_get_all_masters_empty():

    repository = AsyncMock()

    repository.get_all.return_value = []


    service = MasterService(
        repository
    )


    result = await service.get_masters()


    assert result == []


    repository.get_all.assert_called_once()



@pytest.mark.anyio
async def test_get_object_uuid():

    repository = AsyncMock(spec=MasterRepository)

    fake_uuid = uuid.uuid4()

    master = Master(
    id=fake_uuid,
    first_name="Kirill",
    last_name="Test",
    description="Backend",
    experience=3,
    education="IT"
)
    
    repository.get_by_id.return_value = master


    service = MasterService(
        repository
    )


    result = await service.get_master_by_id(fake_uuid)


    assert result == master


    repository.get_by_id.assert_called_once_with(fake_uuid)

    
@pytest.mark.anyio
async def test_get_object_id_not_found():
    repository = AsyncMock()

    fake_id = uuid.uuid4()

    repository.get_by_id.return_value = None

    service = MasterService(
        repository
    )

    result = await service.get_master_by_id(fake_id)


    assert result is None

    repository.get_by_id.assert_called_once_with(fake_id)


@pytest.mark.anyio
async def test_get_master_repository_error():

    repository = AsyncMock(spec=MasterRepository)

    fake_uuid = uuid.uuid4()


    repository.get_by_id.side_effect = Exception(
        "Database error"
    )


    service = MasterService(repository)


    with pytest.raises(Exception):
        await service.get_master_by_id(fake_uuid)


    repository.get_by_id.assert_called_once_with(fake_uuid)


@pytest.mark.anyio
async def test_create():
    repository = AsyncMock()


    master = Master(
        first_name="Kirill",
        last_name="Test",
        description="Backend",
        experience=3,
        education="IT"
    )

    repository.create.return_value = master

    service = MasterService(
        repository
    )

    result = await service.create_master(master)

    assert result == master

    repository.create.assert_awaited_once()

    created_master = repository.create.await_args.args[0]

    assert created_master.first_name == "Kirill"
    assert created_master.experience == 3


# @pytest.mark.anyio
# async def test_create_error():
#     repository = AsyncMock()

#     master = Master(
#         first_name="Kirill",
#         last_name="Test",
#         description="Backend",
#         experience=3,
#         education="IT"
#     )

#     repository.create.side_effect = Exception(
#         "Database error"
#     )

#     service = MasterService(
#         repository
#     )

#     with pytest.raises(HTTPException) as ext: 
#         await service.create_master(master)

#     assert ext.value.status_code == 500
#     assert ext.value.detail == 500


#     repository.assert_awaited_once()



@pytest.mark.anyio
async def test_update_master():

    repository = AsyncMock(spec=MasterRepository)


    fake_uuid = uuid.uuid4()


    master = Master(
        id=fake_uuid,
        first_name="Kirill",
        last_name="Test",
        description="Backend",
        experience=3,
        education="IT"
    )


    repository.get_by_id.return_value = master


    updated_master = Master(
        id=fake_uuid,
        first_name="Kirill",
        last_name="Test",
        description="Backend",
        experience=5,
        education="IT"
    )


    repository.update.return_value = updated_master


    service = MasterService(repository)

    result = await service.update_master(
        fake_uuid,
        MasterUpdate(
            experience=3
        )
)

    assert result == updated_master
    
    repository.get_by_id.assert_awaited_once_with(fake_uuid)

    repository.update.assert_awaited_once()

    update = repository.update.await_args.args[0]

    assert update.experience == 3


@pytest.mark.anyio
async def test_delete_master():

    repository = AsyncMock(spec=MasterRepository)

    fake_uuid = uuid.uuid4()


    master = Master(
        id=fake_uuid,
        first_name="Kirill",
        last_name="Test",
        description="Backend",
        experience=3,
        education="IT"
    )


    repository.get_by_id.return_value = master


    service = MasterService(repository)


    result = await service.delete_master(fake_uuid)


    assert result is True


    repository.get_by_id.assert_awaited_once_with(fake_uuid)

    repository.delete.assert_awaited_once_with(master)


@pytest.mark.anyio
async def test_delete_master_not_found():

    repository = AsyncMock(spec=MasterRepository)


    fake_uuid = uuid.uuid4()


    repository.get_by_id.return_value = None


    service = MasterService(repository)


    result = await service.delete_master(fake_uuid)


    assert result is None


    repository.get_by_id.assert_awaited_once_with(fake_uuid)

    repository.delete.assert_not_awaited()