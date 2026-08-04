import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Master


@pytest.mark.anyio

async def test_get_masters(ac: AsyncClient, create_master: Master):

    response = await ac.get("/masters")

    
    assert response.status_code == 200

    data = response.json()


    assert isinstance(data, list)

    assert len(data) == 1

    master_data = data[0]

    assert master_data["id"] == str(create_master.id)
    assert master_data["first_name"] == create_master.first_name
    assert master_data["last_name"] == create_master.last_name
    assert master_data["description"] == create_master.description
    assert master_data["experience"] == create_master.experience
    assert master_data["education"] == create_master.education
    assert master_data["is_active"] == create_master.is_active



@pytest.mark.anyio
async def test_get_master_invalid_uuid(
    ac: AsyncClient
):
    response = await ac.get(
        "/masters/not-a-uuid"
    )

    assert response.status_code == 422


    data = response.json()

    assert data["detail"][0]["loc"] == [
        "path",
        "master_id"
    ]


@pytest.mark.anyio

async def test_get_master_by_id(ac: AsyncClient, create_master: Master):

    response = await ac.get(f"/masters/{create_master.id}")


    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert data["id"] == str(create_master.id)
    assert data["first_name"] == create_master.first_name
    assert data["last_name"] == create_master.last_name
    assert data["description"] == create_master.description
    


@pytest.mark.anyio
async def test_get_master_not_found(ac: AsyncClient):

    fake_uuid = uuid.uuid4()
    response = await ac.get(f"/masters/{fake_uuid}")


    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Мастер не найден!"


@pytest.mark.anyio
async def test_master_create(ac: AsyncClient, db_session: AsyncSession):
    
    payload = {
        "first_name": "Artem",
        "last_name": "Petrushka",
        "description": "Barmen",
        "experience": 100,
        "education": "FAX"
    }


    response = await ac.post("/masters", json=payload)


    assert response.status_code == 201
    
    data = response.json()

    assert isinstance(data, dict)

    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["description"] == payload["description"]
    assert data["experience"] == payload["experience"]
    assert data["education"] == payload["education"]

    assert "id" in data
    assert "first_name" in data

    master_id = uuid.UUID(data["id"])

    master_database = await db_session.get(
        Master,
        master_id
    )

    assert master_database is not None
    assert master_database.first_name == payload["first_name"]


@pytest.mark.anyio
async def test_create_master_invalid_data(
    ac: AsyncClient
):
    payload = {
        "last_name": "Test",
        "description": "Backend developer",
        "experience": 3,
        "education": "IT"
    }

    response = await ac.post(
        "/masters",
        json=payload
    )

    assert response.status_code == 422

    data = response.json()

    assert isinstance(data["detail"], list)
    assert data["detail"][0]["loc"] == [
        "body",
        "first_name"
    ]

@pytest.mark.anyio
async def test_update_master(ac: AsyncClient, create_master: Master, db_session: AsyncSession):
    
    payload = {
        "first_name": "Artem",
        "experience": 100,
    }


    response = await ac.patch(f"/masters/{create_master.id}", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    
    assert data["first_name"] == "Artem"
    assert data["experience"] == 100

    assert "id" in data
    assert data["id"] == str(create_master.id)
    

    assert data["last_name"] == create_master.last_name


    master_from_database = await db_session.get(
        Master,
        create_master.id
    )

    await db_session.refresh(create_master)

    assert master_from_database.id is not None
    assert master_from_database.id == create_master.id
    assert master_from_database.first_name == payload["first_name"]

@pytest.mark.anyio
async def test_update_master_not_found(
    ac: AsyncClient
):

    fake_uuid = uuid.uuid4()

    payload = {
        "first_name": "Sofia",
        "experience": 1,
    }

    response = await ac.patch(f"/masters/{fake_uuid}", json=payload)

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Мастер не найден!"




@pytest.mark.anyio
async def test_delete_master(create_master, ac: AsyncClient, db_session: AsyncSession):

    master_id = create_master.id
    response = await ac.delete(f"/masters/{master_id}")

    assert response.status_code == 204

    assert response.text == ""

    master_from_database = await db_session.scalar(
        select(Master).where(Master.id==master_id)
    )

    assert master_from_database is None



@pytest.mark.anyio
async def test_delete_master_not_found(ac: AsyncClient):

    fake_uuid = uuid.uuid4()
    response = await ac.delete(f"/masters/{fake_uuid}")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Мастер не найден!"