from fastapi import APIRouter, Depends
from ..dependencies import query_db, toggle_db, delete_db
from ..database import SessionDep
from ..models import Flag, InputFlag
from ..schemas import FlagResponse
router = APIRouter()


@router.get("/flags/")
def get_flags(data= Depends(query_db)):
    return data


@router.post("/flags/")
def create_flag(flag: InputFlag ,session: SessionDep):
    flag_db = Flag(**flag.model_dump())
    session.add(flag_db)
    session.commit()
    session.refresh(flag_db)
    return flag_db

@router.patch("/flags/{environment}/{flag_name}")
def update_flag(data = Depends(toggle_db)):
    print('in')
    return data


@router.delete("/flags/{environment}/{flag_name}")
def delete_flag(result = Depends(delete_db)):
    return result

    