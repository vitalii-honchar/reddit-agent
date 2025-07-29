import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from core.models import AgentConfiguration


class TestAgentConfigurationApiE2E:
    """Test agent configuration endpoints."""

    def test_create_configuration_success(self, client: TestClient, session: Session):
        """Test creating agent configuration - happy flow."""
        # given
        config_data = {
            "agent_type": "search_agent",
            "data": {"search_query": "test query", "max_results": 10}
        }

        # when
        response = client.post("/agent-configurations/", json=config_data)

        # then
        assert response.status_code == 200
        config_id = response.json()
        assert isinstance(uuid.UUID(config_id), uuid.UUID)

        # and
        db_config = session.get(AgentConfiguration, config_id)
        assert db_config is not None
        assert db_config.agent_type == "search_agent"
        assert db_config.data == {"search_query": "test query", "max_results": 10}
        assert db_config.created_at is not None
        assert db_config.updated_at is not None

    def test_get_configuration_success(self, client: TestClient, session: Session):
        """Test getting agent configuration by ID - happy flow."""
        # given
        config = AgentConfiguration(
            agent_type="search_agent",
            data={"search_query": "test", "filters": ["active"]}
        )
        session.add(config)
        session.commit()
        session.refresh(config)

        # when
        response = client.get(f"/agent-configurations/{config.id}")

        # then
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == str(config.id)
        assert response_data["agent_type"] == "search_agent"
        assert response_data["data"] == {"search_query": "test", "filters": ["active"]}
        assert "created_at" in response_data
        assert "updated_at" in response_data

    def test_get_all_configurations_success(self, client: TestClient, session: Session):
        """Test getting all agent configurations - happy flow."""
        # given
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

        # when
        response = client.get("/agent-configurations/")

        # then
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) >= 2

        # and
        ids = {item["id"] for item in response_data}
        assert str(config1.id) in ids
        assert str(config2.id) in ids