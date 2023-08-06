from io import BytesIO
from pathlib import Path
from typing import Optional, TypeVar

from aiofiles.tempfile import TemporaryFile
from aiogoogle.models import MediaDownload
from aiogoogle.models import Request as AiogoogleRequest
from aiogoogle.models import Response as AiogoogleResponse
from tygle.client import Client

from .request import Request

DownloadRequestT = TypeVar("DownloadRequestT", Path, BytesIO)


class DownloadRequest(Request[DownloadRequestT]):
    async def pre_process(self, request: AiogoogleRequest):
        pass

    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ):
        pass


class DownloadToPathRequest(DownloadRequest[Path]):
    def __init__(
        self,
        client: Client,
        request: AiogoogleRequest,
        path: Path,
    ):
        self.path = path
        super().__init__(client, request)

    async def pre_process(self, request: AiogoogleRequest):
        await super().pre_process(request)
        request.media_download = MediaDownload(self.path)

    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ):
        await super().post_process(request, response)
        return self.path


class DownloadToBufferRequest(DownloadRequest[BytesIO]):
    def __init__(
        self,
        client: Client,
        request: AiogoogleRequest,
        buffer: Optional[BytesIO] = None,
    ):
        if buffer:
            self.buffer = buffer
        else:
            self.buffer = BytesIO()
        self.async_buffer = TemporaryFile("wb+")
        super().__init__(client, request)

    async def pre_process(self, request: AiogoogleRequest):
        await super().pre_process(request)
        pipe_to = await self.async_buffer.__aenter__()
        request.media_download = MediaDownload(pipe_to=pipe_to)

    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ):
        await super().post_process(request, response)
        await response.pipe_to.seek(0)
        contents = await response.pipe_to.read()
        self.buffer.write(contents)
        await self.async_buffer.__aexit__(None, None, None)
        return self.buffer
