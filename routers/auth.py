from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from ..database import SessionDep
from ..security import get_password_hash, verify_password
from ..models import User, UserCreate
from ..database import SessionDep
from datetime import timedelta
from ..security import create_access_token


router = APIRouter()



ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5


def authenticate_user(session:SessionDep, username: str, password:str):
    user = session.exec(select(User).where(User.email == username)).scalar()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/signup")
def sign_up(user: UserCreate, session:SessionDep):
    
    new_user = User(
        email=user.email,
        hashed_password = get_password_hash(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return user

@router.post("/login/")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep    
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


    





