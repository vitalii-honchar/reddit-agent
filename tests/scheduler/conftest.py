import os
import subprocess
import threading
import time
from typing import Generator

import pytest
from sqlmodel import Session

from core.models import AgentConfiguration
from scheduler.scheduler_app_context import SchedulerAppContext
from scheduler.settings import SchedulerSettings


def stream_output(proc, prefix="SCHEDULER"):
    """Stream subprocess output in real-time"""

    def reader():
        for line in iter(proc.stdout.readline, ''):
            if line:
                print(f"[{prefix}] {line.rstrip()}")

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    return thread


@pytest.fixture(scope="session")
def settings() -> SchedulerSettings:
    return SchedulerSettings(
        threshold_seconds=1,
    )  # type: ignore


@pytest.fixture(scope="session")
def app_context(settings: SchedulerSettings) -> SchedulerAppContext:
    return SchedulerAppContext(settings)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Launch scheduler with real-time log streaming"""

    print("Starting scheduler subprocess...")

    proc = subprocess.Popen(
        ["python", "-m", "scheduler.main"],
        cwd=os.getcwd(),
        env=os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    stream_output(proc)

    # Check if still alive
    if proc.poll() is not None:
        time.sleep(1)  # Let log thread catch up
        raise RuntimeError(f"Scheduler died with exit code: {proc.returncode}")

    print("Scheduler is running and streaming logs...")

    yield

    print("Terminating scheduler...")
    proc.terminate()

    try:
        proc.wait(timeout=5)
        print("Scheduler terminated gracefully")
    except subprocess.TimeoutExpired:
        print("Force killing scheduler...")
        proc.kill()
        proc.wait()


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
            "search_types": ["reddit"],
        }
    )
    session.add(agent_configuration)
    session.commit()
    session.refresh(agent_configuration)
    return agent_configuration
