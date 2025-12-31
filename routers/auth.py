from fastapi import APIRouter
from pydantic import field_validator, EmailStr
from security import get_password_hash
from ..models import User
router = APIRouter()


@router.post("/signup")
def sign_up(user: User):
    return {
        "email": user.email,
        "password": user.password,
        "hashed_password": get_password_hash(user.password)
    }


