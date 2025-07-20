"""Integration test for Reddit search tool using GPT-4.1"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from praw import Reddit
from langchain_openai import ChatOpenAI
from reddit_agent.tool.reddit.tools import RedditToolsService, create_reddit_search_tool
from reddit_agent.tool.reddit.models import SearchResult


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


@pytest.fixture
def reddit_service(reddit_client, openai_llm):
    """Create Reddit tools service."""
    return RedditToolsService(reddit=reddit_client, llm=openai_llm)


@pytest.fixture
def reddit_search_tool(reddit_service):
    """Create Reddit search tool."""
    return create_reddit_search_tool(reddit_service)


class TestRedditSearchIntegration:
    """Integration tests for Reddit search functionality."""

    def test_search_digital_marketing_opportunities(self, reddit_search_tool):
        """Test searching for digital marketing business opportunities in r/startups."""
        # given
        query = {
            "subreddit": "startups",
            "query": "digital marketing SEO content",
            "limit": 5,
            "filter": {
                "min_score": 5,
                "min_comments": 3,
                "filter_prompt": """Include posts that discuss:
                        - Digital marketing business opportunities
                        - SEO consulting or content creation services
                        - Online marketing strategies for startups
                        - Content marketing and copywriting services
                        Exclude posts about unrelated topics or spam."""
            }
        }

        # when
        result = reddit_search_tool.invoke({
            "query": query
        })

        # then
        search_result = SearchResult.model_validate_json(result)

        assert search_result.subreddit == "startups"
        assert len(search_result.submissions) == 5
        assert all(s.score >= 5 for s in search_result.submissions)
        assert all(s.num_comments >= 3 for s in search_result.submissions)
        assert all(len(s.summary) >= 500 for s in search_result.submissions)
        assert all(len(s.comments_summary) >= 500 for s in search_result.submissions)