from pydantic import field_validator, EmailStr
from typing import Literal, Optional, List
from sqlmodel import SQLModel, Field, AutoString, Relationship
from datetime import datetime, timezone


from uuid import UUID
import uuid


ENV_FLAG = Literal["prod", "stage"]



class UserCreate(SQLModel):
    email: EmailStr
    password: str 
        

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    hashed_password : str
    
    flags: List["Flag"] = Relationship(back_populates="owner")

class FlagBase(SQLModel):
    name: str = Field(max_length=10, index=True)
    environment: ENV_FLAG = Field(sa_type=AutoString)
    is_enabled: bool = False
    description: str 

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc),
    sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)}
    )
    owner_id: int = Field(foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="flags")



