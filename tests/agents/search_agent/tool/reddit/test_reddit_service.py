"""Integration test for Reddit search tool using async"""
import pytest

from ai.search_agent.tool.reddit.models import SearchQuery, SubmissionFilter
from ai.search_agent.tool.reddit import RedditToolsService


class TestRedditService:
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

    @pytest.mark.asyncio
    async def test_search_tech_startup_advice(self, reddit_service: RedditToolsService):
        """Test searching for tech startup advice in r/entrepreneur."""
        # given
        query = SearchQuery(
            subreddit="entrepreneur",
            query="tech startup funding venture capital",
            limit=5,
            filter=SubmissionFilter(
                min_score=10,
                min_comments=5,
                max_days_old=60,
                required_keywords=["startup", "tech"],
                excluded_keywords=["scam", "spam"]
            )
        )

        # when
        search_result = await reddit_service.search(query)

        # then
        assert search_result.subreddit == "entrepreneur"
        assert len(search_result.submissions) <= 5
        assert all(s.score >= 10 for s in search_result.submissions)
        assert all(len(s.comments) >= 0 for s in search_result.submissions)
        # Verify required keywords are present
        for submission in search_result.submissions:
            content = (submission.title + " " + submission.selftext).lower()
            assert "startup" in content
            assert "tech" in content

    @pytest.mark.asyncio
    async def test_search_python_career_opportunities(self, reddit_service: RedditToolsService):
        """Test searching for Python career opportunities in r/Python."""
        # given
        query = SearchQuery(
            subreddit="Python",
            query="career job remote developer",
            limit=4,
            filter=SubmissionFilter(
                min_score=3,
                min_comments=2,
                max_days_old=45,
                min_title_length=15,
                min_content_length=100,
                required_keywords=["python", "career"]
            )
        )

        # when
        search_result = await reddit_service.search(query)

        # then
        assert search_result.subreddit == "Python"
        assert len(search_result.submissions) <= 4
        assert all(s.score >= 3 for s in search_result.submissions)
        assert all(len(s.title) >= 15 for s in search_result.submissions)
        assert all(len(s.selftext) >= 100 for s in search_result.submissions)
        # Verify required keywords
        for submission in search_result.submissions:
            content = (submission.title + " " + submission.selftext).lower()
            assert "python" in content
            assert "career" in content

    @pytest.mark.asyncio
    async def test_search_indie_game_development(self, reddit_service: RedditToolsService):
        """Test searching for indie game development discussions in r/gamedev."""
        # given
        query = SearchQuery(
            subreddit="gamedev",
            query="indie game development unity marketing",
            limit=3,
            filter=SubmissionFilter(
                min_score=8,
                min_comments=4,
                max_days_old=30,
                min_upvote_ratio=0.75,
                excluded_flairs=["Weekly", "Daily"],
                excluded_keywords=["piracy", "cracked"]
            )
        )

        # when
        search_result = await reddit_service.search(query)

        # then
        assert search_result.subreddit == "gamedev"
        assert len(search_result.submissions) <= 3
        assert all(s.score >= 8 for s in search_result.submissions)
        assert all(s.upvote_ratio >= 0.75 for s in search_result.submissions)
        # Verify excluded keywords are not present
        for submission in search_result.submissions:
            content = (submission.title + " " + submission.selftext).lower()
            assert "piracy" not in content
            assert "cracked" not in content