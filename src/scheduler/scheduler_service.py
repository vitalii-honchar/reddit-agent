import logging
from dataclasses import dataclass
from typing import List

from sqlmodel import Session

from models.agent import AgentExecution, SchedulerConfig, utcnow
from repositories.agent import AgentExecutionRepository  
from services.agent import AgentExecutionService
from scheduler.agent_executor import AgentExecutor

logger = logging.getLogger(__name__)


@dataclass
class SchedulerService:
    """
    Service responsible for scheduling and managing agent executions.
    
    Uses optimistic locking with retry limits and cooldown periods to prevent
    infinite execution loops while allowing retries for failed executions.
    """
    
    repository: AgentExecutionRepository
    service: AgentExecutionService
    executor: AgentExecutor
    config: SchedulerConfig = SchedulerConfig()
    
    async def process_pending_executions(self, session: Session) -> int:
        """
        Process all pending executions that are ready for processing.
        
        Returns:
            Number of executions processed in this cycle
        """
        # Find pending executions ready for processing
        pending_executions = self.repository.find_pending(
            session=session,
            limit=100,
            cooldown_seconds=self.config.cooldown_seconds
        )
        
        if not pending_executions:
            logger.debug("No pending executions found")
            return 0
            
        logger.info(f"Found {len(pending_executions)} pending executions")
        processed_count = 0
        
        for execution in pending_executions:
            try:
                if await self._try_process_execution(session, execution):
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing execution {execution.id}: {e}")
                
        return processed_count
    
    async def _try_process_execution(self, session: Session, execution: AgentExecution) -> bool:
        """
        Try to acquire lock and process a single execution.
        
        Returns:
            True if execution was processed, False if lock couldn't be acquired
        """
        # Try to acquire optimistic lock
        locked_execution = self.repository.try_acquire_lock(
            session=session,
            execution_id=execution.id,
            current_executions=execution.executions
        )
        
        if locked_execution is None:
            logger.debug(f"Could not acquire lock for execution {execution.id}")
            return False
            
        logger.info(f"Acquired lock for execution {locked_execution.id} (attempt #{locked_execution.executions})")
        
        # Check if max retries exceeded
        if locked_execution.executions > self.config.max_retries:
            await self._mark_as_failed(session, locked_execution, "Max retries exceeded")
            return True
            
        # Execute the agent
        try:
            await self.executor.execute(locked_execution)
            await self._mark_as_success(session, locked_execution)
            logger.info(f"Successfully executed agent {locked_execution.id}")
            
        except Exception as e:
            error_message = f"Agent execution failed: {str(e)}"
            logger.error(f"Execution {locked_execution.id} failed: {error_message}")
            
            if locked_execution.executions >= self.config.max_retries:
                await self._mark_as_failed(session, locked_execution, error_message)
            else:
                # Leave in pending state for retry, but update timestamp for cooldown
                locked_execution.updated_at = utcnow()
                self.repository.update(session, locked_execution)
                
        return True
    
    async def _mark_as_success(self, session: Session, execution: AgentExecution) -> None:
        """Mark execution as successfully completed."""
        execution.state = "success"
        execution.updated_at = utcnow()
        # TODO: Set success_result when actual agent execution is implemented
        self.repository.update(session, execution)
        
    async def _mark_as_failed(self, session: Session, execution: AgentExecution, error_message: str) -> None:
        """Mark execution as permanently failed."""
        execution.state = "error"
        execution.error_result = {
            "error": error_message,
            "failed_at": utcnow().isoformat(),
            "total_attempts": execution.executions
        }
        execution.updated_at = utcnow()
        self.repository.update(session, execution)
        logger.error(f"Marked execution {execution.id} as failed after {execution.executions} attempts")