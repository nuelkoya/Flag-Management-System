import re
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database import SessionDep
from security import get_password_hash, verify_password
from models import User, UserCreate
from database import SessionDep
from datetime import timedelta
from security import create_access_token
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)




ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
STRONG_PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$"


def authenticate_user(session:SessionDep, username: str, password:str):
    user = session.exec(select(User).where(User.email == username)).scalar()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/signup")
@limiter.limit("10/minutes")
def sign_up(request: Request, user: UserCreate, session:SessionDep):

    if not re.match(STRONG_PASSWORD_REGEX, user.password):
        raise HTTPException(
                status_code=409,
                detail="Password must be at least 8 characters long, "
                "include uppercase, lowercase, a number, and a symbol."
        )

    if session.exec(select(User).where(User.email == user.email)).first():
        raise HTTPException(
            status_code=409,
            detail="Email is already in use."
        )
   

    try:
        new_user = User(
            email=user.email,
            hashed_password = get_password_hash(user.password)
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"user": new_user.email, "message": "User created!"}
    except IntegrityError:
        session.rollback()
        raise HTTPException(
                status_code=409,
                detail="Email is already in use."
        )



  

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


    





