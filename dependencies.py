from fastapi.exceptions import HTTPException
from fastapi import Header, Depends
from typing import Annotated
from fastapi.exceptions import HTTPException
from database import SessionDep
from models import Flag, ENV_FLAG, User
from config import get_settings, Settings
from security import get_current_user
from sqlalchemy import select, func



def verify_admin_token(
    x_admin_token: Annotated[str, Header()],
    settings : Settings = Depends(get_settings)               
):
    if x_admin_token != settings.x_admin_token:
        raise HTTPException(status_code=403, detail="Invalid Secret Header")
    return True 



def get_flags_dep(
    session: SessionDep,
    environment: str | None = None, 
    enabled: bool | None = None,
    offset: int = 0,    # How many records to skip
    limit: int = 10
):
    if not isinstance(offset, int) or not isinstance(limit, int):
        raise TypeError("Offset and Limit must be integers")
    statement = select(Flag)

    if environment:
        statement = statement.where(Flag.environment == environment)
    if enabled is not None:
        statement = statement.where(Flag.is_enabled == enabled)

    statement = statement.offset(offset).limit(limit)
    flag_data = session.exec(statement).scalars().all()
    return flag_data


def toggle_flag(
    session: SessionDep,
    flag_name: str, 
    environment: ENV_FLAG, 
    current_user : Annotated[User, Depends(get_current_user)],
    _: bool = Depends(verify_admin_token),
):
    
    statement = select(Flag).where(
        current_user.id == Flag.owner_id,
        Flag.environment == environment, 
        func.lower(Flag.name) == flag_name.lower(),
        )

    flag = session.exec(statement).scalar()

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found or unauthorized") 
    
    flag.is_enabled = not flag.is_enabled

    session.add(flag)
    session.commit()
    session.refresh(flag)
    return flag



def delete_flag_dep(
    session: SessionDep,
    flag_name: str, 
    environment: ENV_FLAG, 
    current_user : Annotated[User, Depends(get_current_user)],
    _: bool = Depends(verify_admin_token)
):    
    statement = select(Flag).where(
        current_user.id == Flag.owner_id,
        Flag.environment == environment, 
        func.lower(Flag.name) == flag_name)

    flag = session.exec(statement).scalar()

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found or unauthorized ") 
    

    session.delete(flag)
    session.commit()
    return {"ok": True}


           


