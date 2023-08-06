from typing import ClassVar, Type

from pydantic import BaseModel
from tygle_docs.types.responses import UpdateResponse


class UpdateRequest(BaseModel):
    response_type: ClassVar[Type[UpdateResponse]] = UpdateResponse
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents/request#request
    """
