"""Integration test for search agent finding marketing opportunities for indie projects."""
import pytest
from agents.config import Config
from ai.search_agent import SearchResult
from ai.search_agent.models import CreateSearchAgentCommand
from ai.search_agent import execute_search


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
        assert len(result.findings) >= 5, "Should find at least one Reddit search result"

    @pytest.mark.asyncio
    async def test_search_ai_ml_startup_opportunities(self, config: Config):
        """Test searching for AI/ML startup opportunities and trends."""
        # given
        command = CreateSearchAgentCommand(
            behavior="""You are searching for opportunities in the AI/ML startup space.
            
            Focus on:
            - Emerging AI/ML trends and market gaps
            - Funding opportunities for AI startups
            - Technical discussions about AI implementation challenges
            - Posts about AI product launches and user feedback
            - Enterprise AI adoption stories and pain points
            
            Strict restrictions:
            - Only include posts with at least 15 upvotes and 8 comments
            - Focus on actionable insights for AI entrepreneurs
            - Prioritize posts from established AI/ML communities
            - Exclude basic tutorials or beginner questions
            - Look for market validation and business model discussions""",
            search_query="AI ML startup opportunities machine learning business",
            search_types={"reddit"}
        )

        # when
        result = await execute_search(config, command)

        # then
        assert result is not None
        assert isinstance(result, SearchResult)
        assert len(result.findings) >= 3, "Should find AI/ML related results"

    @pytest.mark.asyncio
    async def test_search_saas_product_launch_strategies(self, config: Config):
        """Test searching for SaaS product launch strategies and growth tactics."""
        # given
        command = CreateSearchAgentCommand(
            behavior="""You are researching SaaS product launch strategies and growth tactics.
            
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
            search_query="SaaS product launch strategies customer acquisition growth",
            search_types={"reddit"}
        )

        # when
        result = await execute_search(config, command)

        # then
        assert result is not None
        assert isinstance(result, SearchResult)
        assert len(result.findings) >= 3, "Should find SaaS strategy results"