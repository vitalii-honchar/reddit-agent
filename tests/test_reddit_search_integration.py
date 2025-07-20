"""Integration test for Reddit search tool using GPT-4.1"""
import pytest
from search_agent.tool.reddit.tools import RedditToolsService, create_reddit_search_tool
from search_agent.tool.reddit.models import SearchResult


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
