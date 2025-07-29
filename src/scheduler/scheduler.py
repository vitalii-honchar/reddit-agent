import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import Engine
from sqlmodel import Session

from scheduler.services.scheduler import SchedulerService

logger = logging.getLogger(__name__)


class SchedulerManager:
    """
    Main scheduler manager that handles the event loop and graceful shutdown.
    """

    def __init__(self, poll_interval_seconds: float, scheduler_service: SchedulerService, db_engine: Engine):
        self.shutdown_event = asyncio.Event()
        self.poll_interval_seconds = poll_interval_seconds
        self.db_engine = db_engine
        self.scheduler_service = scheduler_service

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Session, None]:
        session = Session(self.db_engine)
        try:
            yield session
        finally:
            session.close()

    async def run_scheduler_loop(self):
        logger.info(f"Starting scheduler with poll_interval = {self.poll_interval_seconds} s")
        while not self.shutdown_event.is_set():
            try:
                async with self.get_session() as session:
                    await self.scheduler_service.process_pending_executions(session)
            except Exception:
                logger.exception(f"Unexpected error")
            await asyncio.sleep(self.poll_interval_seconds)

        logger.info("Scheduler loop stopped")

    async def start(self):
        logger.info("Starting agent execution scheduler...")

        try:
            await self.run_scheduler_loop()
        except Exception as e:
            logger.critical(f"Scheduler failed with unhandled exception: {e}")
            raise
        finally:
            logger.info("Scheduler shutdown complete")
