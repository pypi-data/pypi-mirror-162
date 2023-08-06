from typing import TYPE_CHECKING, Callable, Optional

from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ClientCreds, ServiceAccountCreds, UserCreds
from aiogoogle.models import Response as AiogoogleResponse

if TYPE_CHECKING:
    from tygle.base.requests import Request


class Client:
    """
    Proxy for interaction with Aiogoogle.
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        user_creds: Optional[UserCreds] = None,
        client_creds: Optional[ClientCreds] = None,
        service_account_creds: Optional[ServiceAccountCreds] = None,
    ) -> None:
        self.aiogoogle = Aiogoogle(
            api_key=api_key,
            user_creds=user_creds,
            client_creds=client_creds,
            service_account_creds=service_account_creds,
        )

    async def __aenter__(self, *args):
        await self.aiogoogle.__aenter__(*args)
        return self.aiogoogle

    async def __aexit__(self, *args):
        await self.aiogoogle.__aexit__(*args)

    async def __execute(
        self, method: Callable, request: "Request"
    ) -> AiogoogleResponse:
        async with self as c:
            response = await method(c, request.request, full_res=True)
        return response

    async def as_api_key(self, request: "Request"):
        return await self.__execute(Aiogoogle.as_api_key, request)

    async def as_user(self, request: "Request"):
        return await self.__execute(Aiogoogle.as_user, request)

    async def as_service_account(self, request: "Request"):
        return await self.__execute(Aiogoogle.as_service_account, request)

    async def as_anon(self, request: "Request"):
        return await self.__execute(Aiogoogle.as_anon, request)
