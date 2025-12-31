from pydantic import field_validator, EmailStr
from typing import Annotated, Literal
from sqlmodel import SQLModel, Field, AutoString

from uuid import UUID
import uuid


ENV_FLAG = Literal["prod", "stage"]

class FlagBase(SQLModel):
    name: str = Field(max_length=10, index=True)
    environment: ENV_FLAG = Field(sa_type=AutoString)
    is_enabled: bool = False
    description: str 

    model_config = {
        "from_attributes": True  # This is the "Magic" fix for serialization
    }

    @field_validator("name")
    @classmethod
    def check_alphabeth(cls, v: str) -> str:
        if v.isdigit():
            raise ValueError("Flag name cannot be a number")
        return v
   


class InputFlag(FlagBase):
    pass 

class Flag(FlagBase, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class User(SQLModel, table=True):
    email: EmailStr = Field(primary_key=True)
    password : str