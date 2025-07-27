from typing import Generator

import pytest
from sqlmodel import Session

from core.models import AgentConfiguration
from scheduler.main import app_context


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Database session fixture using the same Postgres database as agentapi tests."""
    with Session(app_context.db_engine) as session:
        yield session


@pytest.fixture
def agent_configuration(session: Session) -> AgentConfiguration:
    agent_configuration = AgentConfiguration(
        agent_type="search_agent",
        data={
            "behavior": """You are researching SaaS product launch strategies and growth tactics.
                Focus on:
                - Successful SaaS product launch case studies
                - Customer acquisition strategies for B2B SaaS
                - Pricing strategies and revenue model discussions
                - Product-market fit validation techniques
                - Growth hacking tactics specific to SaaS companies
                
                Strict restrictions:
                - Only include posts with at least 20 upvotes and 10 comments
                - Focus on proven strategies with measurable results
                - Prioritize posts from experienced SaaS founders
                - Exclude generic marketing advice not SaaS-specific
                - Look for posts with concrete metrics and outcomes""",
            "search_query": "SaaS product launch strategies customer acquisition growth",
            "search_types": "reddit",
        }
    )
    session.add(agent_configuration)
    session.commit()
    session.refresh(agent_configuration)
    return agent_configuration
