import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient
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


class TestAgentExecutionApiE2E:
    """Test agent execution endpoints."""

    @pytest.mark.asyncio
    async def test_create_execution_success(self, client: TestClient, session: Session, agent_configuration: AgentConfiguration):
        """Test creating agent execution - happy flow and verify scheduler processes it."""
        # given
        execution_id = uuid.uuid4()
        execution_data = {
            "id": str(execution_id),
            "config_id": str(agent_configuration.id)
        }

        # when
        response = client.post("/agent-executions/", json=execution_data)

        # then
        assert response.status_code == 200
        returned_id = response.json()
        assert returned_id == str(execution_id)

        # and
        db_execution = session.get(AgentExecution, execution_id)
        assert db_execution is not None
        assert db_execution.config_id == agent_configuration.id
        assert db_execution.state == "pending"  # default state
        assert db_execution.executions == 0  # default value
        assert db_execution.created_at is not None
        assert db_execution.updated_at is not None
        assert db_execution.success_result is None
        assert db_execution.error_result is None

        # and - verify scheduler processes the execution
        await wait_execution_state(session, db_execution, "completed", timeout=180) # type: ignore

        session.refresh(db_execution)
        assert db_execution.state == "completed"
        assert "findings" in db_execution.success_result
        assert "metadata" in db_execution.success_result
        assert len(db_execution.success_result["findings"]) >= 1
        assert db_execution.error_result is None
        assert db_execution.executions >= 1
        assert db_execution.updated_at > db_execution.created_at

    def test_get_execution_success(self, client: TestClient, session: Session):
        """Test getting agent execution by ID - happy flow."""
        # given
        config = AgentConfiguration(
            agent_type="search_agent",
            data={"search_query": "test"}
        )
        session.add(config)
        session.commit()
        session.refresh(config)

        execution = AgentExecution(
            config_id=config.id,
            executions=3,
            success_result={"results": ["item1", "item2"]},
            error_result=None
        )
        session.add(execution)
        session.commit()
        session.refresh(execution)

        # when
        response = client.get(f"/agent-executions/{execution.id}")

        # then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(execution.id)
        assert response_data["config_id"] == str(config.id)
        assert response_data["executions"] == 3
        assert response_data["success_result"] == {"results": ["item1", "item2"]}
        assert response_data["error_result"] is None
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_create_execution_with_existing_config_success(self, client: TestClient, session: Session):
        """Test creating execution with valid config reference - happy flow."""
        # given
        config = AgentConfiguration(
            agent_type="search_agent",
            data={"filters": ["hot", "rising"]}
        )
        session.add(config)
        session.commit()
        session.refresh(config)

        execution_id = uuid.uuid4()
        execution_data = {
            "id": str(execution_id),
            "config_id": str(config.id)
        }

        # when
        response = client.post("/agent-executions/", json=execution_data)

        # then
        assert response.status_code == 200

        # and
        db_execution = session.get(AgentExecution, execution_id)
        assert db_execution is not None
        assert db_execution.config_id == config.id

        # and
        db_config = session.get(AgentConfiguration, config.id)
        assert db_config is not None
        assert db_config.id == db_execution.config_id
