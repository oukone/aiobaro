import pathlib
from collections import namedtuple

import pytest

from aiobaro.core import MatrixClient

from .utils import is_responsive


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return (
        pathlib.Path(pytestconfig.rootdir) / "tests/docker/docker-compose.yml"
    )


@pytest.fixture(scope="session")
def matrix_server_url(docker_ip, docker_services) -> str:
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("matrix", 8008)
    url = f"http://{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_responsive(f"{url}/_matrix/client/versions"),
    )
    return url


@pytest.fixture(scope="session")
def matrix_client(matrix_server_url):
    return MatrixClient(matrix_server_url)


@pytest.fixture(scope="function")
async def seed_data(matrix_client):
    class SeedData(namedtuple("SeedData", ["room", "users", "devices"])):
        __slots__ = ()

    users = [
        await matrix_client.register(
            f"seed_user_{i}", password="seed_password"
        )
        for i in {1, 2}
    ]
    await matrix_client.login("seed_user_1", password="seed_password")
    devices = await matrix_client.devices()
    return SeedData(
        room=None,
        users=users,
        devices=devices,
    )
