from typing import Optional

from pydantic import BaseModel, Field


class WriteControl(BaseModel):
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents/batchUpdate#WriteControl
    """

    required_revision_id: Optional[str] = Field(None, alias="requiredRevisionId")
    target_revision_id: Optional[str] = Field(None, alias="targetRevisionId")
