import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import Engine
from sqlmodel import Session

from scheduler.scheduler_app_context import SchedulerAppContext
from scheduler.services.scheduler import SchedulerService
from scheduler.settings import SchedulerSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

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

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

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
        self.setup_signal_handlers()

        logger.info("Starting agent execution scheduler...")

        try:
            await self.run_scheduler_loop()
        except Exception as e:
            logger.critical(f"Scheduler failed with unhandled exception: {e}")
            raise
        finally:
            logger.info("Scheduler shutdown complete")


settings = SchedulerSettings()  # type: ignore
app_context = SchedulerAppContext(settings)
scheduler_manager = SchedulerManager(
    settings.poll_interval_seconds,
    app_context.scheduler_service,
    app_context.db_engine,
)

if __name__ == "__main__":
    try:
        asyncio.run(scheduler_manager.start())
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Scheduler failed to start: {e}")
        sys.exit(1)
