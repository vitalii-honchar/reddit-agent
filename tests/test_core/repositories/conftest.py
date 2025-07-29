from typing import Generator

import pytest
from sqlmodel import Session

from agentapi.dependencies import ctx
from core.models.agent import AgentConfiguration
from core.repositories.agent import AgentExecutionRepository


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Create a test database session using the same context as API tests."""
    with Session(ctx.db_engine) as session:
        yield session


@pytest.fixture
def agent_config(session: Session):
    """Create a test agent configuration."""
    config = AgentConfiguration(
        agent_type="search_agent",
        data={"test": "data"}
    )
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


@pytest.fixture
def repository():
    """Create AgentExecutionRepository instance."""
    return AgentExecutionRepository()