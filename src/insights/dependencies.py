from .app_context import create_app_context
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends

from .services import AgentAPIService

ctx = create_app_context()


def get_session():
    with Session(ctx.db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
AgentApiServiceDep = Annotated[AgentAPIService, Depends(lambda: ctx.agent_api_service)]

__all__ = ["ctx", "SessionDep", "AgentApiServiceDep"]
