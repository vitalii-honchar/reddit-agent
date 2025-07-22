"""Integration test for Reddit search tool using async"""
import pytest

from search_agent.tool.reddit.models import SearchQuery, SubmissionFilter
from search_agent.tool.reddit.tools import RedditToolsService


class TestRedditSearchIntegration:
    """Integration tests for Reddit search functionality."""

    @pytest.mark.asyncio
    async def test_search_digital_marketing_opportunities(self, reddit_service: RedditToolsService):
        """Test searching for digital marketing business opportunities in r/startups."""
        # given
        query = SearchQuery(
            subreddit="startups",
            query="digital marketing SEO content",
            limit=3,
            filter=SubmissionFilter(
                min_score=5,
                min_comments=3,
                max_days_old=90
            )
        )

        # when
        search_result = await reddit_service.search(query)

        # then
        assert search_result.subreddit == "startups"
        assert len(search_result.submissions) <= 3
        assert all(s.score >= 5 for s in search_result.submissions)
        assert all(len(s.comments) >= 0 for s in search_result.submissions)
        assert all(len(s.title) > 0 for s in search_result.submissions)
        assert all(len(s.selftext) > 0 for s in search_result.submissions)