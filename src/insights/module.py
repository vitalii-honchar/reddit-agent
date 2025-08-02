import asyncio
import threading
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlmodel import create_engine, Session
from typing import Annotated
from fastapi import Depends

from app.app_module import AppModule
from .settings import InsightsConfig
from insights.services import AgentAPIService, AgentConfigurationService
from insights.scheduler import InsightsScheduler
from insights import routes


class InsightsModule(AppModule):
    """Insights module for web frontend"""
    
    def __init__(self, config: InsightsConfig):
        self.config = config
        self.db_engine = create_engine(config.db_url, echo=config.debug)
        self.agent_api_service = AgentAPIService(config.agent_api_base_url)
        self.logger = logging.getLogger("uvicorn")
        self.agent_configuration_service = AgentConfigurationService(self.agent_api_service, self.logger)
        self.scheduler = InsightsScheduler(
            timeout_seconds=config.insights_scheduler_timeout,
            logger=self.logger,
            base_url=config.agent_api_base_url,
        )
    
    def get_session(self):
        with Session(self.db_engine) as session:
            yield session
    
    async def on_startup(self) -> None:
        """Startup logic for Insights module"""
        await self.agent_configuration_service.migrate()
        if self.config.scheduler_enabled:
            threading.Thread(
                target=lambda: asyncio.run(self.scheduler.start()),
                daemon=True
            ).start()
    
    async def on_shutdown(self) -> None:
        """Shutdown logic for Insights module"""
        if self.config.scheduler_enabled:
            await self.scheduler.stop()
    
    def init(self, app: FastAPI) -> None:
        """Initialize the Insights module"""
        
        # Mount static files
        app.mount("/static", StaticFiles(directory="static"), name="static")
        
        # Add routes
        app.include_router(routes.insights)
        app.include_router(routes.health)
        
        # Add dependencies
        SessionDep = Annotated[Session, Depends(self.get_session)]
        AgentApiServiceDep = Annotated[AgentAPIService, Depends(lambda: self.agent_api_service)]