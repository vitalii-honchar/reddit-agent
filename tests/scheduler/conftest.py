import asyncio
from typing import Generator

import pytest
import pytest_asyncio
from sqlmodel import Session

from core.models import AgentConfiguration
from scheduler.main import SchedulerManager
from scheduler.scheduler_app_context import SchedulerAppContext
from scheduler.settings import SchedulerSettings


@pytest.fixture(scope="session")
def settings() -> SchedulerSettings:
    return SchedulerSettings(
        threshold_seconds=1,
    )  # type: ignore


@pytest.fixture(scope="session")
def app_context(settings: SchedulerSettings) -> SchedulerAppContext:
    return SchedulerAppContext(settings)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_environment(app_context: SchedulerAppContext, settings: SchedulerSettings):
    """Automatically setup/teardown scheduler for entire test session."""
    # Setup - start scheduler in background
    scheduler_manager = SchedulerManager(
        settings.poll_interval_seconds,
        app_context.scheduler_service,
        app_context.db_engine,
    )
    scheduler_task = asyncio.create_task(scheduler_manager.start())
    await asyncio.sleep(0.1)  # Give scheduler time to start

    yield  # Run all tests

    # Teardown - stop scheduler gracefully
    scheduler_manager.shutdown_event.set()
    try:
        await asyncio.wait_for(scheduler_task, timeout=5.0)
    except asyncio.TimeoutError:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass


@pytest.fixture
def session(app_context: SchedulerAppContext) -> Generator[Session, None, None]:
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
