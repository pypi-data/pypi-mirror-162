from typing import List

from pydantic import BaseModel, Field
from tygle_docs.types.write_control import WriteControl

from .update_response import UpdateResponse


class BatchUpdateResponse(BaseModel):
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents/batchUpdate#response-body
    """

    document_id: str = Field(alias="documentId")
    replies: List[UpdateResponse] = Field()
    write_control: WriteControl = Field(alias="writeControl")
