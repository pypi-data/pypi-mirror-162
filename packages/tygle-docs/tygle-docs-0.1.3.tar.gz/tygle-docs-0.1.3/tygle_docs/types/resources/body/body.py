from typing import List

from pydantic import BaseModel, Field

from .structural_element import StructuralElement


class Body(BaseModel):
    content: List[StructuralElement] = Field()
