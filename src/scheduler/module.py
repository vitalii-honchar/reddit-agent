import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import create_engine, Session
from typing import AsyncGenerator

from app.app_module import AppModule
from .settings import SchedulerConfig
from core.repositories import AgentExecutionRepository, AgentConfigurationRepository
from core.services import AgentExecutionService, AgentConfigurationService
from scheduler.services import AgentExecutor, SchedulerService

logger = logging.getLogger("uvicorn")


class SchedulerModule(AppModule):
    """Scheduler module for background processing"""
    
    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.db_engine = create_engine(config.db_url, echo=config.debug)
        self.shutdown_event = asyncio.Event()
        self.scheduler_task = None
        
        # Initialize components
        self.agent_executor = AgentExecutor(config)
        self.agent_execution_repository = AgentExecutionRepository()
        self.agent_configuration_repository = AgentConfigurationRepository()
        self.agent_configuration_service = AgentConfigurationService(self.agent_configuration_repository)
        self.agent_execution_service = AgentExecutionService(
            self.agent_execution_repository,
            self.agent_configuration_service
        )
        self.scheduler_service = SchedulerService(
            execution_service=self.agent_execution_service,
            executor=self.agent_executor,
            settings=config,
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Session, None]:
        session = Session(self.db_engine)
        try:
            yield session
        finally:
            session.close()
    
    async def run_scheduler_loop(self):
        logger.info(f"Starting scheduler with poll_interval = {self.config.poll_interval_seconds} s")
        while not self.shutdown_event.is_set():
            try:
                async with self.get_session() as session:
                    await self.scheduler_service.process_pending_executions(session)
            except Exception:
                logger.exception(f"Unexpected error")
            await asyncio.sleep(self.config.poll_interval_seconds)
        
        logger.info("Scheduler loop stopped")
    
    async def start_scheduler(self):
        logger.info("Starting agent execution scheduler...")
        
        try:
            await self.run_scheduler_loop()
        except Exception as e:
            logger.critical(f"Scheduler failed with unhandled exception: {e}")
            raise
        finally:
            logger.info("Scheduler shutdown complete")
    
    async def on_startup(self) -> None:
        """Startup logic for Scheduler module"""
        # Start scheduler as background task
        self.scheduler_task = asyncio.create_task(self.start_scheduler())
    
    async def on_shutdown(self) -> None:
        """Shutdown logic for Scheduler module"""
        # Shutdown scheduler
        self.shutdown_event.set()
        try:
            await asyncio.wait_for(self.scheduler_task, timeout=30.0)
        except asyncio.TimeoutError:
            logger.warning("Scheduler shutdown timed out")
            self.scheduler_task.cancel()
    
    def init(self, app: FastAPI) -> None:
        """Initialize the Scheduler module"""
        # Scheduler module doesn't add any routes or middleware
        # All functionality is handled via startup/shutdown lifecycle
        pass