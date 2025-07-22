"""Integration test for search agent finding marketing opportunities for indie projects."""
import pytest
from config import Config
from search_agent import SearchResult
from search_agent.models import CreateSearchAgentCommand
from search_agent.search_agent import execute_search


class TestSearchAgentIntegration:
    """Integration tests for search agent functionality."""

    @pytest.mark.asyncio
    async def test_search_indie_project_marketing_opportunities(self, config: Config):
        """Test searching for marketing opportunities for indie projects with strict restrictions."""
        # given
        command = CreateSearchAgentCommand(
            behavior="""You are searching for marketing opportunities specifically for indie projects.
            
            Focus on:
            - Subreddits where indie developers and creators share their work
            - Communities discussing indie project marketing strategies
            - Posts about promoting indie games, apps, or creative projects
            - Marketing channels and strategies that work for small budgets
            - Community building for indie creators
            
            Strict restrictions:
            - Only include posts with at least 10 upvotes and 5 comments
            - Focus on actionable marketing advice, not just general discussion
            - Prioritize recent posts (within last month)
            - Exclude spam, self-promotion without value, or irrelevant content
            - Look for posts with practical tips, case studies, or success stories""",
            search_query="marketing opportunities for indie projects and small creators",
            search_types={"reddit"}
        )

        # when
        result = await execute_search(config, command)

        # then
        assert result is not None
        assert isinstance(result, SearchResult)
        assert len(result.reddit_search_results) >= 5, "Should find at least one Reddit search result"