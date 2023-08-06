from typing import ClassVar

from pydantic import BaseModel, Field
from tygle_docs.types.responses import ReplaceAllTextResponse

from .update_request import UpdateRequest


class SubstringMatchCriteria(BaseModel):
    text: str = Field()
    match_case: bool = Field(alias="matchCase")


class ReplaceAllText(BaseModel):
    replace_text: str = Field(alias="replaceText")
    contains_text: SubstringMatchCriteria = Field(alias="containsText")


class ReplaceAllTextRequest(UpdateRequest):
    response_type: ClassVar = ReplaceAllTextResponse
    replace_all_text: ReplaceAllText = Field(alias="replaceAllText")
