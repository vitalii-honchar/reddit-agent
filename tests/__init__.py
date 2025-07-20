import pytest
from pathlib import Path
from dotenv import load_dotenv
from praw import Reddit
from langchain_openai import ChatOpenAI
import os


@pytest.fixture
def reddit_client():
    """Create Reddit client from environment variables."""
    # Load .env from project root using pathlib for better cross-platform support
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"

    # Try to load .env file if it exists
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Also try to load from current working directory
        load_dotenv()

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        pytest.skip("Reddit API credentials not configured")

    return Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )


@pytest.fixture
def openai_llm():
    """Create OpenAI GPT-4.1 client."""
    # Load .env from project root using pathlib for better cross-platform support
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"

    # Try to load .env file if it exists
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Also try to load from current working directory
        load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OpenAI API key not configured")

    return ChatOpenAI(
        model="gpt-4.1",
        temperature=0.1,
        api_key=api_key
    )
