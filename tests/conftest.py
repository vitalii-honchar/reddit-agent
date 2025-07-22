import os
from pathlib import Path
from typing import Callable, AsyncGenerator

import asyncpraw
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from config import Config
from search_agent.tool.reddit.tools import RedditToolsService, create_reddit_search_tool


@pytest_asyncio.fixture
async def reddit_client(config: Config) -> AsyncGenerator[asyncpraw.Reddit, None]:
    reddit = asyncpraw.Reddit(
        client_id=config.reddit_config.client_id,
        client_secret=config.reddit_config.client_secret,
        user_agent=config.reddit_config.user_agent
    )
    yield reddit
    await reddit.close()

@pytest.fixture
def config() -> Config:
    """Create config with Reddit and LLM setup."""
    from config.config import RedditConfig
    
    # Load environment variables for Reddit config
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"

    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")
    api_key = os.getenv("OPENAI_API_KEY")

    if not all([client_id, client_secret, user_agent, api_key]):
        pytest.fail("credentials not configured")

    reddit_config = RedditConfig(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    return Config(
        llm=ChatOpenAI(
            model="gpt-4.1",
            temperature=0.1,
            api_key=api_key
        ),
        reddit_config=reddit_config
    )

@pytest_asyncio.fixture
async def reddit_service(reddit_client) -> AsyncGenerator[RedditToolsService, None]:
    """Create Reddit tools service."""
    yield RedditToolsService(reddit=reddit_client)
