import pytest


pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.client",
    "tests.fixtures.masters",
]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"