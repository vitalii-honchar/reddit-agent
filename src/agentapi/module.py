import asyncio
import threading
from fastapi import FastAPI
from sqlmodel import create_engine, Session
from typing import Annotated
from fastapi import Depends

from app.app_module import AppModule
from .settings import AgentAPIConfig
from scheduler.settings import SchedulerConfig
from core.repositories import AgentConfigurationRepository, AgentExecutionRepository
from core.services import AgentConfigurationService, AgentExecutionService
from scheduler.scheduler import SchedulerManager
from scheduler.scheduler_app_context import SchedulerAppContext
from agentapi import routes


class AgentAPIModule(AppModule):
    """AgentAPI module for REST API backend"""
    
    def __init__(self, config: AgentAPIConfig, scheduler_config: SchedulerConfig):
        self.config = config
        self.scheduler_config = scheduler_config
        self.db_engine = create_engine(config.db_url, echo=config.debug)
        
        # Initialize repositories and services
        self.agent_configuration_repository = AgentConfigurationRepository()
        self.agent_execution_repository = AgentExecutionRepository()
        self.agent_configuration_service = AgentConfigurationService(self.agent_configuration_repository)
        self.agent_execution_service = AgentExecutionService(
            self.agent_execution_repository,
            self.agent_configuration_service
        )
        
        # Initialize scheduler components
        self.scheduler_ctx = SchedulerAppContext(scheduler_config)
        self.scheduler_manager = SchedulerManager(
            scheduler_config.poll_interval_seconds,
            self.scheduler_ctx.scheduler_service,
            self.scheduler_ctx.db_engine,
        )
    
    def get_session(self):
        with Session(self.db_engine) as session:
            yield session
    
    async def on_startup(self) -> None:
        """Startup logic for AgentAPI module"""
        scheduler_thread = threading.Thread(
            target=lambda: asyncio.run(self.scheduler_manager.start()),
            daemon=True
        )
        scheduler_thread.start()
    
    async def on_shutdown(self) -> None:
        """Shutdown logic for AgentAPI module"""
        self.scheduler_manager.shutdown_event.set()
    
    def init(self, app: FastAPI) -> None:
        """Initialize the AgentAPI module"""
        
        # Add routes
        app.include_router(routes.agent_configurations)
        app.include_router(routes.agent_executions)
        app.include_router(routes.health)
        
        # Add dependencies
        SessionDep = Annotated[Session, Depends(self.get_session)]
        AgentConfigurationServiceDep = Annotated[AgentConfigurationService, Depends(lambda: self.agent_configuration_service)]
        AgentExecutionServiceDep = Annotated[AgentExecutionService, Depends(lambda: self.agent_execution_service)]