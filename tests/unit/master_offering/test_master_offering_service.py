import uuid
from unittest.mock import AsyncMock

import pytest
from decimal import Decimal
from src.master_offering.models import MasterOffering
from src.master_offering.repository import MasterOfferingRepository
from src.master_offering.schemas import MasterOfferingUpdate, MasterOfferingCreate
from src.master_offering.service import MasterOfferingService




@pytest.mark.anyio
async def test_get_object_uuid():

    repository = AsyncMock(spec=MasterOfferingRepository)

    fake_uuid = uuid.uuid4()

    offering = MasterOffering(
        id=fake_uuid,
        title="Стрижка для волос",
        description="ВЦВЦВ",
        price=Decimal("113.00"),
        duration_minutes=100
)
    
    repository.get_by_id.return_value = offering


    service = MasterOfferingService(
        repository
    )


    result = await service.get_offering_by_id(fake_uuid)


    assert result == offering


    repository.get_by_id.assert_called_once_with(fake_uuid)

    
@pytest.mark.anyio
async def test_get_object_id_not_found():
    repository = AsyncMock()

    fake_id = uuid.uuid4()

    repository.get_by_id.return_value = None

    service = MasterOfferingService(
        repository
    )

    result = await service.get_offering_by_id(fake_id)


    assert result is None

    repository.get_by_id.assert_called_once_with(fake_id)


@pytest.mark.anyio
async def test_get_master_repository_error():

    repository = AsyncMock(spec=MasterOfferingRepository)

    fake_uuid = uuid.uuid4()


    repository.get_by_id.side_effect = Exception(
        "Database error"
    )


    service = MasterOfferingService(repository)


    with pytest.raises(Exception):
        await service.get_offering_by_id(fake_uuid)


    repository.get_by_id.assert_called_once_with(fake_uuid)


@pytest.mark.anyio
async def test_create():
    repository = AsyncMock(
        spec=MasterOfferingRepository
    )

    master_id = uuid.uuid4()

    data = MasterOfferingCreate(
        title="Стрижка для волос",
        description="ВЦВЦВ",
        price=Decimal("113.00"),
        duration_minutes=100,
    )

    created_offering = MasterOffering(
        master_id=master_id,
        title=data.title,
        description=data.description,
        price=data.price,
        duration_minutes=data.duration_minutes,
    )

    repository.create.return_value = created_offering

    service = MasterOfferingService(repository)

    result = await service.create_offering(
        master_id,
        data,
    )

    assert result == created_offering

    repository.create.assert_awaited_once()

    offering_to_create = repository.create.await_args.args[0]

    assert offering_to_create.master_id == master_id
    assert offering_to_create.title == data.title
    assert offering_to_create.price == data.price
    assert offering_to_create.duration_minutes == 100


@pytest.mark.anyio
async def test_update_master():

    repository = AsyncMock(spec=MasterOfferingRepository)


    fake_uuid = uuid.uuid4()


    offering = MasterOffering(
        id=fake_uuid,
        title="Стрижка для волос",
        description="ВЦВЦВ",
        price=Decimal("113.00"),
        duration_minutes=100
    )


    repository.get_by_id.return_value = offering


    updated_master = MasterOffering(
        id=fake_uuid,
        title="Стрижка для волос",
        description="ВЦВЦВ",
        price=Decimal("115.00"),
        duration_minutes=150
    )


    repository.update.return_value = updated_master


    service = MasterOfferingService(repository)

    result = await service.update_offering(
        fake_uuid,
        MasterOfferingUpdate(
            duration_minutes=100
        )
)

    assert result == updated_master
    
    repository.get_by_id.assert_awaited_once_with(fake_uuid)

    repository.update.assert_awaited_once()

    update = repository.update.await_args.args[0]

    assert update.duration_minutes == 100


@pytest.mark.anyio
async def test_delete_master():

    repository = AsyncMock(spec=MasterOfferingRepository)

    fake_uuid = uuid.uuid4()


    offering = MasterOffering(
        id=fake_uuid,
        title="Стрижка для волос",
        description="ВЦВЦВ",
        price=Decimal("113.00"),
        duration_minutes=100
    )


    repository.get_by_id.return_value = offering


    service = MasterOfferingService(repository)


    result = await service.delete_offering(fake_uuid)


    assert result is True


    repository.get_by_id.assert_awaited_once_with(fake_uuid)

    repository.delete.assert_awaited_once_with(offering)


@pytest.mark.anyio
async def test_delete_master_not_found():

    repository = AsyncMock(spec=MasterOfferingRepository)


    fake_uuid = uuid.uuid4()


    repository.get_by_id.return_value = None


    service = MasterOfferingService(repository)


    result = await service.delete_offering(fake_uuid)


    assert result is None


    repository.get_by_id.assert_awaited_once_with(fake_uuid)

    repository.delete.assert_not_awaited()