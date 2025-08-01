import os
from pathlib import Path
from typing import AsyncGenerator

import asyncpraw
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agents.config import Config, RedditConfig
from agents.search_agent.tool.reddit.tools import RedditToolsService


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
    # Load environment variables for Reddit config
    project_root = Path(__file__).parent.parent.parent.parent
    env_path = project_root / ".env"

    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    client_id = os.getenv("INDIE_HACKERS_AGENT_REDDIT_CLIENT_ID")
    client_secret = os.getenv("INDIE_HACKERS_AGENT_REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("INDIE_HACKERS_AGENT_REDDIT_AGENT")
    api_key = os.getenv("INDIE_HACKERS_AGENT_OPENAI_API_KEY")

    if not all([client_id, client_secret, user_agent, api_key]):
        pytest.fail("credentials not configured")

    reddit_config = RedditConfig(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    # Set prompt folder path
    prompt_folder = project_root / "prompts"

    return Config(
        llm=ChatOpenAI(
            model="gpt-4.1",
            temperature=0.1,
            api_key=api_key
        ),
        reddit_config=reddit_config,
        prompts_folder=prompt_folder
    )

@pytest_asyncio.fixture
async def reddit_service(reddit_client) -> AsyncGenerator[RedditToolsService, None]:
    """Create Reddit tools service."""
    yield RedditToolsService(reddit=reddit_client)
