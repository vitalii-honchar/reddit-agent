import logging
from dataclasses import dataclass

from sqlmodel import Session

from core.models.agent import AgentExecution, utcnow
from core.services.agent import AgentExecutionService
from scheduler.services.agent_executor import AgentExecutor
from scheduler.settings import SchedulerSettings
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SchedulerService:
    execution_service: AgentExecutionService
    executor: AgentExecutor
    settings: SchedulerSettings

    async def process_pending_executions(self, session: Session) -> int:
        pending_executions = self.execution_service.find_pending(
            session=session,
            threshold=self.settings.threshold_seconds
        )

        if not pending_executions:
            return 0

        logger.info(f"Found {len(pending_executions)} pending executions")
        processed_count = 0

        for execution in pending_executions:
            try:
                if await self._try_process_execution(session, execution):
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing execution {execution.id}: {e}")

        logger.info(f"Processed {processed_count} pending executions")
        return processed_count

    async def _try_process_execution(self, session: Session, execution: AgentExecution) -> bool:
        locked_execution = self.execution_service.acquire_lock(session, execution)

        if locked_execution is None:
            return False

        logger.info(f"Acquired lock for execution {locked_execution.id} (attempt #{locked_execution.executions})")

        if locked_execution.executions > self.settings.max_retries:
            await self._mark_as_failed(session, locked_execution, "Max retries exceeded")
            return True

        try:
            execution_res = await self.executor.execute(locked_execution)
            await self._mark_as_completed(session, locked_execution, execution_res)
            logger.info(f"Successfully executed agent {locked_execution.id}")
        except Exception as e:
            logger.exception(f"Execution {locked_execution.id} failed")

            locked_execution.error_result = {"error": str(e)}
            self.execution_service.update(session, execution)
        return True

    async def _mark_as_completed(self, session: Session, execution: AgentExecution, res: dict[str, Any]) -> None:
        execution.state = "completed"
        execution.updated_at = utcnow()
        execution.success_result = res
        self.execution_service.update(session, execution)

    async def _mark_as_failed(self, session: Session, execution: AgentExecution, error_message: str) -> None:
        execution.state = "failed"
        if execution.error_result is None:
            execution.error_result = {
                "error": error_message,
            }
        self.execution_service.update(session, execution)
        logger.error(f"Marked execution {execution.id} as failed after {execution.executions} attempts")
