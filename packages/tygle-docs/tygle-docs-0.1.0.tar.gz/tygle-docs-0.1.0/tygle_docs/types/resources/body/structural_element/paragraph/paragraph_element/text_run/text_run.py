from typing import List

from pydantic import BaseModel, Field


class TextRun(BaseModel):
    content: str
    suggested_insertion_ids: List[str] = Field(alias="suggestedInsertionIds")
    suggested_deletion_ids: List[str] = Field(alias="suggestedDeletionIds")
