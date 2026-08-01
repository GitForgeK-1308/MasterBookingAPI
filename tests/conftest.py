import pytest


pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.client",
    "tests.fixtures.masters",
    "tests.fixtures.master_offering",
]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"