import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlmodel import Session

from app_context import create_app_context
from core.models.agent import SchedulerConfig
from core.repositories.agent import AgentExecutionRepository
from core.services.agent import AgentExecutionService
from scheduler.services.agent_executor import AgentExecutor
from scheduler.services.scheduler import SchedulerService

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
    
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.config = SchedulerConfig()
        
        # Initialize app context and dependencies
        self.app_context = create_app_context()
        self.repository = self.app_context.agent_execution_repository
        self.service = self.app_context.agent_execution_service
        self.executor = AgentExecutor()
        self.scheduler_service = SchedulerService(
            repository=self.repository,
            service=self.service,
            executor=self.executor,
            config=self.config
        )
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[Session, None]:
        """Get database session with proper cleanup."""
        session = Session(self.app_context.db_engine)
        try:
            yield session
        finally:
            session.close()
    
    async def run_scheduler_loop(self):
        """
        Main scheduler loop that processes pending executions every poll_interval seconds.
        """
        logger.info(
            f"Starting scheduler with poll_interval={self.config.poll_interval}s, "
            f"max_retries={self.config.max_retries}, cooldown_seconds={self.config.cooldown_seconds}s"
        )
        
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while not self.shutdown_event.is_set():
            try:
                async with self.get_session() as session:
                    processed_count = await self.scheduler_service.process_pending_executions(session)
                    
                    if processed_count > 0:
                        logger.info(f"Processed {processed_count} executions")
                    else:
                        logger.debug("No executions processed this cycle")
                        
                # Reset error counter on successful cycle
                consecutive_errors = 0
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Scheduler cycle failed (error #{consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.critical(f"Too many consecutive errors ({consecutive_errors}), shutting down")
                    self.shutdown_event.set()
                    break
                    
                # Exponential backoff on errors
                error_sleep_time = min(30, 2 ** consecutive_errors)
                logger.info(f"Sleeping {error_sleep_time}s before retry")
                await asyncio.sleep(error_sleep_time)
                continue
            
            # Wait for next polling cycle or shutdown signal
            try:
                await asyncio.wait_for(
                    self.shutdown_event.wait(), 
                    timeout=self.config.poll_interval
                )
                # If we get here, shutdown was requested
                break
            except asyncio.TimeoutError:
                # Normal timeout, continue to next cycle
                pass
        
        logger.info("Scheduler loop stopped")
    
    async def start(self):
        """Start the scheduler with proper setup and cleanup."""
        self.setup_signal_handlers()
        
        logger.info("Starting agent execution scheduler...")
        
        try:
            await self.run_scheduler_loop()
        except Exception as e:
            logger.critical(f"Scheduler failed with unhandled exception: {e}")
            raise
        finally:
            logger.info("Scheduler shutdown complete")


async def main():
    """Main entry point for the scheduler."""
    scheduler_manager = SchedulerManager()
    await scheduler_manager.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Scheduler failed to start: {e}")
        sys.exit(1)