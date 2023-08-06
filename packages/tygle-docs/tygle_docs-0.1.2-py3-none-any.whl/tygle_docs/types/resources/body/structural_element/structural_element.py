from typing import Optional

from pydantic import BaseModel, Field

from .paragraph import Paragraph


class StructuralElement(BaseModel):
    start_index: int = Field(alias="startIndex")
    end_index: int = Field(alias="endIndex")
    paragraph: Optional[Paragraph] = Field(None)
    # section_break: Optional[] = Field(None, alias="sectionBreak")
    # table: Optional[] = Field(None)
    # table_of_contents: Optional[] = Field(None, alias="tableOfContents")
