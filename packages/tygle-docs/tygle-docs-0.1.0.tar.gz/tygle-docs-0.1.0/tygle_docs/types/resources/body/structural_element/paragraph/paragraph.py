from typing import List

from pydantic import BaseModel, Field

from .paragraph_element import ParagraphElement


class Paragraph(BaseModel):
    elements: List[ParagraphElement] = Field()
