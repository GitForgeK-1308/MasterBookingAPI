import uuid
import pytest
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from src.masters.models import Master
from src.master_offering.models import MasterOffering
from tests.fixtures.database import db_session



@pytest.mark.anyio

async def test_get_offering_by_id(create_offering: MasterOffering, ac: AsyncClient):

    response = await ac.get(f"/offerings/{create_offering.id}")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert data["id"] == str(create_offering.id)
    assert data["title"] == create_offering.title
    assert data["description"] == create_offering.description
    assert Decimal(data["price"]) == create_offering.price
    assert data["duration_minutes"] == create_offering.duration_minutes
    

@pytest.mark.anyio

async def test_get_offering_not_found(ac: AsyncClient):

    fake_id = uuid.uuid4()

    response = await ac.get(f"/offerings/{fake_id}")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Услуга не найдена!"


@pytest.mark.anyio

async def test_create_offering(create_master: Master, db_session: AsyncSession, ac: AsyncClient):
    payload = {
        "title": "Artem",
        "description": "Petrushka",
        "price": 10,
        "duration_minutes": 100,
    }


    response = await ac.post(f"/masters/{create_master.id}/offerings", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert isinstance(data, dict)

    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert Decimal(data["price"]) == payload["price"]
    assert data["duration_minutes"] == payload["duration_minutes"]


    assert "id" in data 

    offering_id = uuid.UUID(data["id"])

    offering_from_database = await db_session.get(
        MasterOffering,
        offering_id,
    )

    assert offering_from_database is not None
    assert offering_from_database.master_id == create_master.id
    assert offering_from_database.master_id == create_master.id
    assert offering_from_database.title == payload["title"]
    assert offering_from_database.description == payload["description"]
    assert offering_from_database.price == Decimal("10.00")
    assert (
        offering_from_database.duration_minutes
        == payload["duration_minutes"]
    )


# @pytest.mark.anyio
# async def test_create_master_invalid_data(
#     ac: AsyncClient
# ):
#     payload = {
#         "last_name": "Test",
#         "description": "Backend developer",
#         "experience": 3,
#         "education": "IT"
#     }

#     response = await ac.post(
#         "/masters",
#         json=payload
#     )

#     assert response.status_code == 422

#     data = response.json()

#     assert isinstance(data["detail"], list)
#     assert data["detail"][0]["loc"] == [
#         "body",
#         "first_name"
#     ]


