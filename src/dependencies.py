from app_context import create_app_context
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends

ctx = create_app_context()

def get_session():
    with Session(ctx.db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

__all__ = [
    "SessionDep",
]