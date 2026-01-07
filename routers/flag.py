from fastapi import APIRouter, Depends, Request
from typing import Annotated
from ..dependencies import get_flags, toggle_flag, delete_flag, verify_admin_token
from ..database import SessionDep
from ..models import Flag, InputFlag, User
from ..schemas import FlagResponse, OuterFlag, BulkFlagResponse
from ..security import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/flags/", response_model=BulkFlagResponse)
@limiter.limit("10/minutes")
def get_flags(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    data= Depends(get_flags),
):

    return {
        "message": "Flags",
        "items": data
    }


@router.post("/flags/", response_model=OuterFlag)
def create_flag(
    flag: InputFlag,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    _ : str = Depends(verify_admin_token)
):
    
    new_flag = Flag(**flag.model_dump(), owner_id=current_user.id)
    session.add(new_flag)
    session.commit()
    session.refresh(new_flag)
    return new_flag

@router.patch("/flags/{environment}/{flag_name}", response_model=OuterFlag)
def update_flag(data = Depends(toggle_flag)):
    return data


@router.delete("/flags/{environment}/{flag_name}")
def delete_flag(result = Depends(delete_flag)):
    return result

    