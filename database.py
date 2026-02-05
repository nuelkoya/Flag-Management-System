from sqlmodel import Session, SQLModel, Field, create_engine, select
from fastapi import Depends
from typing import Annotated
from config import Settings, get_settings
from uuid import UUID
import uuid

settings = get_settings()

sqlite_url = settings.database_url
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
