from pprint import pprint

from requests import Response as RequestsResponse


class BaseResponse(object):
    """Обертка для ответа от тестируемого приложения"""

    response: RequestsResponse
    context: dict

    def __init__(self, response: RequestsResponse, context: dict) -> None:
        self.response = response
        self.context = context

        assert 'client' in context
        assert 'request' in context

    @property
    def json(self):
        try:
            return self.response.json()

        except TypeError:
            pass

    def pprint(self):
        pprint(['response object', self.response])
        pprint(['json', self.json])


class AssertTools(BaseResponse):
    def assert_status(self, *status_codes: int):
        if not status_codes:
            status_codes = (200,)

        assert self.response.status_code in status_codes, 'Неожиданный код ответа "{0}" (ожидались "{1}"): {2}'.format(
            self.response.status_code, ','.join(status_codes), self.json
        )

    def assert_not_status(self, *status_codes: int):
        assert len(status_codes)

        assert (
            self.response.status_code not in status_codes
        ), 'Неожиданный код ответа "{0}" (ожидались не "{1}"): {2}'.format(
            self.response.status_code, ','.join(status_codes), self.json
        )


class Response(AssertTools):
    """Обертка для ответа от тестируемого приложения"""
