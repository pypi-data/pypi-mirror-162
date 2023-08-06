from typing import Any, Union

QueryParams = list[tuple[str, str]]
QueryParamsAgile = Union[dict[str, str], list[tuple[str, str]]]


class Request(object):
    """Объект, описывающий данные запроса"""

    method: str
    path: str
    query_params: QueryParams | None
    body: dict | None
    headers: dict

    def __init__(
        self,
        method: str,
        path: str,
        query_params: QueryParamsAgile | None = None,
        body: Any = None,
        headers: dict = None,
    ) -> None:
        if isinstance(query_params, dict):
            query_params = list(query_params.items())

        self.method = method
        self.path = path
        self.query_params = query_params
        self.body = body
        self.headers = headers
