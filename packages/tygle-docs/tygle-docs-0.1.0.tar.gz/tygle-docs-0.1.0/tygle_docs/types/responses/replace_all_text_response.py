from pydantic import BaseModel, Field

from .update_response import UpdateResponse


class ReplaceAllText(BaseModel):
    occurences_changed: int = Field(alias="occurrencesChanged")


class ReplaceAllTextResponse(UpdateResponse):
    replace_all_text: ReplaceAllText = Field(alias="replaceAllText")
