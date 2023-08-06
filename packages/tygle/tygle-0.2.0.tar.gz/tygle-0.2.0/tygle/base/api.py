from aiogoogle import GoogleAPI
from tygle.client import Client


class API:
    api_name: str
    api_version: str

    def __init__(self, client: Client, api: GoogleAPI):
        self.client = client
        self.api = api

    @classmethod
    async def connect(cls, client: Client):
        async with client as c:
            return await c.discover(cls.api_name, cls.api_version)

    @classmethod
    async def new(cls, client: Client):
        api = await cls.connect(client)
        return cls(client, api)
