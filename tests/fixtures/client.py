from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from src.database.session import get_async_session
from src.main import app
from tests.fixtures.database import TestSessionLocal


@pytest.fixture
async def ac(
    prepare_test_database,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_async_session():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[
        get_async_session
    ] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.pop(
        get_async_session,
        None,
    )