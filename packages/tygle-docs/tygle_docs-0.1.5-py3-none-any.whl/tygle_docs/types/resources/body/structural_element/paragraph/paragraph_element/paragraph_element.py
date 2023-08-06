from typing import Optional

from pydantic import BaseModel, Field

from .text_run import TextRun


class ParagraphElement(BaseModel):
    start_index: int = Field(alias="startIndex")
    end_index: int = Field(alias="endIndex")
    text_run: Optional[TextRun] = Field(None, alias="textRun")
