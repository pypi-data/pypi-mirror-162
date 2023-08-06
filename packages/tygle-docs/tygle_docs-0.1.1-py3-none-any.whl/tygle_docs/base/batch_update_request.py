from typing import Generic, Type

from aiogoogle.models import Request as AiogoogleRequest
from aiogoogle.models import Response as AiogoogleResponse
from tygle.base.requests import DataRequest
from tygle.base.requests.data_request import DataT
from tygle.client import Client
from tygle_docs.types.requests import BatchUpdateBody


class BatchUpdateRequest(DataRequest, Generic[DataT]):
    def __init__(
        self,
        client: Client,
        request: AiogoogleRequest,
        resource_type: Type[DataT],
        batch_update_request: BatchUpdateBody,
    ):
        self.batch_update_request = batch_update_request
        super().__init__(client, request, resource_type)

    async def pre_process(self, request: AiogoogleRequest):
        return await super().pre_process(request)

    async def post_process(
        self, request: AiogoogleRequest, response: AiogoogleResponse
    ):
        parsed_replies = []
        for update_request, reply in zip(
            self.batch_update_request.requests, response.json.get("replies", [])
        ):
            parsed_replies.append(update_request.response_type.parse_obj(reply))
        response.json["replies"] = parsed_replies
        return await super().post_process(request, response)
