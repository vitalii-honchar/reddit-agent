import asyncio

import pytest
from sqlmodel import Session

from core.models.agent import AgentConfiguration, AgentExecution, AgentExecutionState


async def wait_until(condition_func, timeout=10.0, poll_interval=0.1):
    """Wait until condition_func() returns True or timeout expires"""
    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < timeout:
        if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
            return True
        await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Condition not met within {timeout} seconds")


async def wait_execution_state(
        session: Session,
        execution: AgentExecution,
        state: AgentExecutionState,
        timeout: float = 10) -> AgentExecution:
    def is_finished():
        session.refresh(execution)
        return execution.state == state

    await wait_until(is_finished, timeout=timeout)

    return execution


class TestSchedulerE2E:

    @pytest.mark.asyncio
    async def test_scheduler_processes_execution_with_success_result(
            self,
            session: Session,
            agent_configuration: AgentConfiguration,
    ):
        # given
        expected_res = {}

        # when
        execution = AgentExecution(
            config_id=agent_configuration.id,
            state="pending",
            executions=0,
        )
        session.add(execution)
        session.commit()
        session.refresh(execution)

        # then
        await wait_execution_state(session, execution, "completed", timeout=180)

        session.refresh(execution)
        assert execution.state == "completed"
        assert "findings" in execution.success_result
        assert "metadata" in execution.success_result
        assert len(execution.success_result["findings"]) >= 1
        assert execution.error_result is None
        assert execution.executions >= 1
        assert execution.updated_at > execution.created_at

    # @pytest.mark.asyncio
    # async def test_scheduler_processes_execution_with_failure_result(
    #     self,
    #     session: Session,
    #     scheduler_service: SchedulerService,
    #     agent_config: AgentConfiguration
    # ):
    #     """Test scheduler processes execution and writes failure result to database."""
    #     # Given: Create AgentExecution in pending state
    #     execution_id = uuid.uuid4()
    #     execution = AgentExecution(
    #         id=execution_id,
    #         config_id=agent_config.id,
    #         state="pending",
    #         executions=0,
    #         updated_at=utcnow()
    #     )
    #     session.add(execution)
    #     session.commit()
    #     session.refresh(execution)
    #
    #     # Given: Mock failed execution
    #     error_message = "Reddit API rate limit exceeded"
    #     scheduler_service.executor.execute.side_effect = Exception(error_message)
    #
    #     # When: Process the execution
    #     await scheduler_service.process_pending_executions(session)
    #
    #     # Then: Verify execution was updated with error result
    #     session.refresh(execution)
    #     assert execution.state == "pending"  # Still pending for retry
    #     assert execution.success_result is None
    #     assert execution.error_result == {"error": error_message}
    #     assert execution.executions == 1  # Should be incremented
    #     assert execution.updated_at > execution.created_at
    #
    #     # Then: Verify executor was called with correct execution
    #     scheduler_service.executor.execute.assert_called_once()
    #     called_execution = scheduler_service.executor.execute.call_args[0][0]
    #     assert called_execution.id == execution_id
