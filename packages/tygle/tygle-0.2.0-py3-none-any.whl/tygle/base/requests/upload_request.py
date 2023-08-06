from io import BytesIO
from pathlib import Path
from typing import Optional, Type

from aiogoogle.models import Request as AiogoogleRequest
from aiogoogle.models import Response as AiogoogleResponse
from tygle.client import Client

from .data_request import DataRequest, DataT


class UploadRequest(DataRequest):
    def __init__(
        self,
        client: Client,
        request: AiogoogleRequest,
        *,
        resource_type: Optional[Type[DataT]] = None,
    ):
        super().__init__(client, request, resource_type)


class UploadFromPathRequest(UploadRequest):
    def __init__(
        self,
        client: Client,
        request: AiogoogleRequest,
        path: Path,
        *,
        resource_type: Optional[Type[DataT]] = None,
    ):
        self.path = path
        super().__init__(client, request, resource_type=resource_type)

    async def pre_process(self, request: AiogoogleRequest):
        await super().pre_process(request)
        request.media_upload.file_path = self.path

    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ):
        return await super().post_process(request, response)


class UploadFromBufferRequest(UploadRequest):
    def __init__(
        self,
        client: Client,
        request: AiogoogleRequest,
        buffer: BytesIO,
        *,
        resource_type: Optional[Type[DataT]] = None,
    ):
        self.buffer = buffer
        super().__init__(client, request, resource_type=resource_type)

    async def pre_process(self, request: AiogoogleRequest):
        await super().pre_process(request)
        # Workaround until https://github.com/omarryhan/aiogoogle/issues/98 is solved
        request.media_upload.file_body = self.buffer.read()
        request.media_upload.pipe_from = None

    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ):
        return await super().post_process(request, response)
