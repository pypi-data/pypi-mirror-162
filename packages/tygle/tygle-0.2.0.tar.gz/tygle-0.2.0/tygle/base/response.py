from typing import Any, Generic, TypeVar

from .requests import Request

RequestT = TypeVar("RequestT", bound=Request)


class Response(Generic[RequestT]):
    def __init__(self, request: RequestT, data: Any) -> None:
        self.request = request
        self.data = data
