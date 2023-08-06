from urllib.parse import urlparse

from pytest_rest_api.logger import logger
from pytest_rest_api.requests import Request
from pytest_rest_api.responses import Response


class ClientConfiguration(object):
    """База для конфигурации клиента"""

    protocol: str
    host: str
    base_path: str

    URL_SETTINGS_FIELDS = ('protocol', 'host', 'base_path')
    REQUIRED_SETTINGS_FIELDS = ('protocol', 'host')

    def __init__(self) -> None:
        self.protocol = 'http'
        self.base_path = '/'

    def parse_base_url(self, base_url: str):
        parse_result = urlparse(base_url)

        self.protocol = parse_result.scheme if parse_result.scheme else self.protocol
        self.host = parse_result.netloc if parse_result.netloc else self.host
        self.base_path = parse_result.path if parse_result.path else self.base_path

        logger.debug(
            'Декомпозиция base_url="%s" на: protocol="%s"; host="%s"; base_path="%s"',
            base_url,
            self.protocol,
            self.host,
            self.base_path,
        )

    def applying_settings(self, settings: dict):

        base_url = settings.get('url')
        if base_url is not None:
            self.parse_base_url(base_url)

        else:
            for field in self.URL_SETTINGS_FIELDS:
                self_value = getattr(self, field, None)
                new_value = settings.get(field, self_value)
                setattr(self, field, new_value)

        if self.base_path is not None and self.base_path[0] != '/':
            self.base_path = f'/{self.base_path}'

        if self.host is not None:
            self.host = self.host.removesuffix('/')

    def check_settings(self):
        self.applying_settings({})

        for field in self.SETTINGS_FIELDS:
            if getattr(self, field, None) is None:
                raise ValueError(f'В объекта клиента "{repr(self)}" не установлено обаятельное поле: {field}')


class BaseClient(ClientConfiguration):
    """Клиент для отправки запросов"""

    def implement_request(self, request: Request):
        pass


class ToolsClientMixin(object):
    """Класс, реализующий вспомогательные инструменты для клиента"""


class MethodsClientMixin(object):
    """Класс, основные методы запросов"""

    request_class: type[Request] = Request
    response_class: type[Response] = Response

    def make_request(self, *args, **kwargs) -> Response:
        return self.request_class(*args, **kwargs)

    def request(self, *args, **kwargs) -> Response:
        request = self.make_request(*args, **kwargs)
        return self.implement_request(request)

    def get(self, *args, **kwargs) -> Response:
        request = self.make_request('get', *args, **kwargs)
        return self.implement_request(request)

    def post(self, *args, **kwargs) -> Response:
        request = self.make_request('post', *args, **kwargs)
        return self.implement_request(request)

    def put(self, *args, **kwargs) -> Response:
        request = self.make_request('put', *args, **kwargs)
        return self.implement_request(request)

    def patch(self, *args, **kwargs) -> Response:
        request = self.make_request('patch', *args, **kwargs)
        return self.implement_request(request)

    def delete(self, *args, **kwargs) -> Response:
        request = self.make_request('delete', *args, **kwargs)
        return self.implement_request(request)


class Client(MethodsClientMixin, ToolsClientMixin, BaseClient):
    """Клиент для отправки запросов"""


class AsyncClient(Client):
    """Асинхронный эквивалент клиента `Client`"""
