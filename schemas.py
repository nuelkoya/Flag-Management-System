from pydantic import BaseModel, Field
from typing import Annotated

from uuid import UUID
import uuid




class OuterFlag(BaseModel):
    name: Annotated[str, Field(max_length=10, strip_whitespace=True)]
    is_enabled: bool | None = False
    environment: str
    description: str 

class FlagResponse(BaseModel):
    message: str
    details: OuterFlag

class BulkFlagResponse(BaseModel):
    message: str
    environment: str
    enabled: bool | None = None
    items: list[OuterFlag] 