from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from aiogoogle.models import Request as AiogoogleRequest
from aiogoogle.models import Response as AiogoogleResponse
from tygle.client import Client

RequestT = TypeVar("RequestT")


class Request(Generic[RequestT], metaclass=ABCMeta):
    def __init__(self, client: Client, request: AiogoogleRequest):
        self.client = client
        self.request = request

    @abstractmethod
    async def pre_process(self, request: AiogoogleRequest):
        raise NotImplementedError

    @abstractmethod
    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ) -> RequestT:
        raise NotImplementedError

    async def as_api_key(self):
        await self.pre_process(self.request)
        response = await self.client.as_api_key(self)
        return await self.post_process(self.request, response)

    async def as_user(self):
        await self.pre_process(self.request)
        response = await self.client.as_user(self)
        return await self.post_process(self.request, response)

    async def as_service_account(self):
        await self.pre_process(self.request)
        response = await self.client.as_service_account(self)
        return await self.post_process(self.request, response)

    async def as_anon(self):
        await self.pre_process(self.request)
        response = await self.client.as_anon(self)
        return await self.post_process(self.request, response)
