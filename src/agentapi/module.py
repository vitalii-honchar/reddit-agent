import asyncio
import threading
from fastapi import FastAPI
from sqlmodel import create_engine, Session
from typing import Annotated
from fastapi import Depends

from app.app_module import AppModule
from .settings import AgentAPIConfig
from core.repositories import AgentConfigurationRepository, AgentExecutionRepository
from core.services import AgentConfigurationService, AgentExecutionService
from agentapi import routes


class AgentAPIModule(AppModule):
    """AgentAPI module for REST API backend"""

    def __init__(self):
        self.config = AgentAPIConfig()  # type: ignore
        self.db_engine = create_engine(self.config.db_url, echo=self.config.debug)

        # Initialize repositories and services
        self.agent_configuration_repository = AgentConfigurationRepository()
        self.agent_execution_repository = AgentExecutionRepository()
        self.agent_configuration_service = AgentConfigurationService(self.agent_configuration_repository)
        self.agent_execution_service = AgentExecutionService(
            self.agent_execution_repository,
            self.agent_configuration_service
        )

    def init(self, app: FastAPI):
        app.include_router(routes.agent_configurations)
        app.include_router(routes.agent_executions)
        app.include_router(routes.health)


agentApiModule = AgentAPIModule()


def get_session():
    with Session(agentApiModule.db_engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
AgentConfigurationServiceDep = Annotated[
    AgentConfigurationService, Depends(lambda: agentApiModule.agent_configuration_service)]
AgentExecutionServiceDep = Annotated[AgentExecutionService, Depends(lambda: agentApiModule.agent_execution_service)]

__all__ = ["agentApiModule", "SessionDep", "AgentConfigurationService", "AgentExecutionService"]
