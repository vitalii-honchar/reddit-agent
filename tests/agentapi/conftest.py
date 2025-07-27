from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from agentapi.dependencies import ctx
from agentapi.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def session() -> Generator[Session, None, None]:
    with Session(ctx.db_engine) as session:
        yield session