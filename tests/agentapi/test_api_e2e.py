import pytest
import uuid
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from agentapi.main import app
from agentapi.dependencies import get_session
from core.models.agent import AgentConfiguration, AgentExecution


@pytest.fixture(name="session")
def session_fixture():
    """Create test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with database session override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAgentConfigurationAPI:
    """Test agent configuration endpoints."""

    def test_create_configuration_success(self, client: TestClient, session: Session):
        """Test creating agent configuration - happy flow."""
        # Arrange
        config_data = {
            "agent_type": "search_agent",
            "data": {"search_query": "test query", "max_results": 10}
        }

        # Act
        response = client.post("/agent-configurations/", json=config_data)

        # Assert HTTP response
        assert response.status_code == 200
        config_id = response.json()
        assert isinstance(uuid.UUID(config_id), uuid.UUID)

        # Assert database changes
        db_config = session.get(AgentConfiguration, config_id)
        assert db_config is not None
        assert db_config.agent_type == "search_agent"
        assert db_config.data == {"search_query": "test query", "max_results": 10}
        assert db_config.created_at is not None
        assert db_config.updated_at is not None

    def test_get_configuration_success(self, client: TestClient, session: Session):
        """Test getting agent configuration by ID - happy flow."""
        # Arrange - create configuration in database
        config = AgentConfiguration(
            agent_type="search_agent",
            data={"search_query": "test", "filters": ["active"]}
        )
        session.add(config)
        session.commit()
        session.refresh(config)

        # Act
        response = client.get(f"/agent-configurations/{config.id}")

        # Assert HTTP response
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(config.id)
        assert response_data["agent_type"] == "search_agent"
        assert response_data["data"] == {"search_query": "test", "filters": ["active"]}
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_get_all_configurations_success(self, client: TestClient, session: Session):
        """Test getting all agent configurations - happy flow."""
        # Arrange - create multiple configurations in database
        config1 = AgentConfiguration(
            agent_type="search_agent",
            data={"query": "test1"}
        )
        config2 = AgentConfiguration(
            agent_type="search_agent",
            data={"query": "test2"}
        )
        session.add_all([config1, config2])
        session.commit()
        session.refresh(config1)
        session.refresh(config2)

        # Act
        response = client.get("/agent-configurations/")

        # Assert HTTP response
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2
        
        # Assert database data integrity
        config_ids = {item["id"] for item in response_data}
        assert str(config1.id) in config_ids
        assert str(config2.id) in config_ids
        
        for item in response_data:
            assert item["agent_type"] == "search_agent"
            assert "data" in item
            assert "created_at" in item
            assert "updated_at" in item


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