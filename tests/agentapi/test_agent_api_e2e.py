import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from core.models.agent import AgentConfiguration, AgentExecution



class TestAgentExecutionAPI:
    """Test agent execution endpoints."""

    def test_create_execution_success(self, client: TestClient, session: Session):
        """Test creating agent execution - happy flow."""
        # Arrange - create configuration first
        config = AgentConfiguration(
            agent_type="search_agent",
            data={"search_query": "test"}
        )
        session.add(config)
        session.commit()
        session.refresh(config)

        execution_id = uuid.uuid4()
        execution_data = {
            "id": str(execution_id),
            "config_id": str(config.id)
        }

        # Act
        response = client.post("/agent-executions/", json=execution_data)

        # Assert HTTP response
        assert response.status_code == 200
        returned_id = response.json()
        assert returned_id == str(execution_id)

        # Assert database changes
        db_execution = session.get(AgentExecution, execution_id)
        assert db_execution is not None
        assert db_execution.config_id == config.id
        assert db_execution.state == "pending"  # default state
        assert db_execution.executions == 0  # default value
        assert db_execution.created_at is not None
        assert db_execution.updated_at is not None
        assert db_execution.success_result is None
        assert db_execution.error_result is None

    def test_get_execution_success(self, client: TestClient, session: Session):
        """Test getting agent execution by ID - happy flow."""
        # Arrange - create configuration and execution in database
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

        # Act
        response = client.get(f"/agent-executions/{execution.id}")

        # Assert HTTP response
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
        # Arrange
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

        # Act
        response = client.post("/agent-executions/", json=execution_data)

        # Assert HTTP response
        assert response.status_code == 200

        # Assert database relationship integrity
        db_execution = session.get(AgentExecution, execution_id)
        assert db_execution is not None
        assert db_execution.config_id == config.id
        
        # Verify the configuration still exists and is linked
        db_config = session.get(AgentConfiguration, config.id)
        assert db_config is not None
        assert db_config.id == db_execution.config_id