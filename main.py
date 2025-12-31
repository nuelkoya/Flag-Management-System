from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from .routers import flag_router,auth
from .database import SessionDep, create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    print("Database Initialized!")
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)
app.include_router(flag_router.router)
app.include_router(auth.router)


@app.exception_handler(RequestValidationError)
async def flag_exception(request: Request, exc: RequestValidationError):
    return  JSONResponse(
        status_code=400,
        content= {
            "status": "error",
            "error": exc.errors(),
            #"error": str(exc.errors()[0]["msg"]),
            "body": exc.body
        }    
    )

@app.get("/")
def root(session: SessionDep):
    return f"Welcome to this flag project{session}"






