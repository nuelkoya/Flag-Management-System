from fastapi.exceptions import HTTPException
from fastapi import Header, Depends
from typing import Annotated
from fastapi.exceptions import HTTPException
from .database import SessionDep
from .models import Flag, ENV_FLAG
from sqlalchemy import select, func


def verify_admin_token(x_admin_token: Annotated[str, Header()]):
    if x_admin_token != "secret-key":
        raise HTTPException(status_code=403, detail="Token value is incorrect!!")
    return True 



def query_db(
        session: SessionDep,
        environment: str | None = None, 
        enabled: bool | None = None,
        offset: int = 0,    # How many records to skip
        limit: int = 10
    ):

    statement = select(Flag)

    if environment:
        statement = statement.where(Flag.environment == environment)
    if enabled is not None:
        statement = statement.where(Flag.is_enabled == enabled)

    statement = statement.offset(offset).limit(limit)
    flag_data = session.exec(statement).scalars().all()
    return flag_data


def toggle_db(
        session: SessionDep,
        flag_name: str, 
        environment: ENV_FLAG, 
        _: bool = Depends(verify_admin_token)):
    
    statement = select(Flag).where(Flag.environment == environment, func.lower(Flag.name) == flag_name.lower())

    flag = session.exec(statement).scalar()

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found") 
    
    flag.is_enabled = not flag.is_enabled

    session.add(flag)
    session.commit()
    session.refresh(flag)
    return flag



def delete_db(
        session: SessionDep,
        flag_name: str, 
        environment: ENV_FLAG, 
        _: bool = Depends(verify_admin_token)):    
    print("innnnn")
    statement = select(Flag).where(Flag.environment == environment, func.lower(Flag.name) == flag_name)

    flag = session.exec(statement).scalar()

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found") 
    
    session.delete(flag)
    session.commit()

    return {"ok": True}
    

           


