import pytest

from pytest_rest_api.clients import Client, AsyncClient


@pytest.fixture(scope='function')
def client_configuration() -> dict:
    """Фикстура определения глобальных настроек клиентов `pytest_rest_api.clients`

    Returns:
        dict: _description_

    """

    return {}


@pytest.fixture(scope='function')
def client(client_configuration) -> Client:  # noqa: WPS442
    """Клиент для HTTP запросов

    Args:
        client_configuration (_type_): _description_

    Returns:
        Client: Объект клиента

    """

    new_client = Client()
    new_client.applying_settings(client_configuration)

    return new_client


@pytest.fixture(scope='function')
def aclient(client_configuration) -> AsyncClient:  # noqa: WPS442
    """Асинхронный эквивалент фикстуры `client`

    Args:
        client_configuration (_type_): _description_

    Returns:
        AsyncClient: Объект клиента

    """

    new_a_client = AsyncClient()
    new_a_client.applying_settings(client_configuration)

    return new_a_client
