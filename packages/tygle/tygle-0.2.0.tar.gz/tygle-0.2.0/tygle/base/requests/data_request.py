from typing import Type, TypeVar

from aiogoogle.models import Request as AiogoogleRequest
from aiogoogle.models import Response as AiogoogleResponse
from pydantic import BaseModel
from tygle.client import Client

from .request import Request

DataT = TypeVar("DataT", bound=BaseModel)


class DataRequest(Request[DataT]):
    def __init__(
        self,
        client: Client,
        request: AiogoogleRequest,
        resource_type: Type[DataT],
    ):
        self.resource_type = resource_type
        super().__init__(client, request)

    async def pre_process(self, request: AiogoogleRequest):
        pass

    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ):
        return self.resource_type.parse_obj(response.json)
