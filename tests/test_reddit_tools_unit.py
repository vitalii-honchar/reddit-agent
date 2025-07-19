"""Unit tests for Reddit tools that don't require external API calls."""
from unittest.mock import Mock
from datetime import datetime
from reddit_agent.tool.reddit.tools import RedditToolsService, create_reddit_search_tool
from reddit_agent.tool.reddit.models import SearchQuery, SubmissionFilter, RedditSubmission


class TestRedditToolsService:
    """Unit tests for RedditToolsService."""
    
    def test_create_reddit_search_tool(self):
        """Test that create_reddit_search_tool returns a callable function."""
        # Mock dependencies
        mock_reddit = Mock()
        mock_llm = Mock()
        service = RedditToolsService(reddit=mock_reddit, llm=mock_llm)
        
        # Create the tool
        tool = create_reddit_search_tool(service)
        
        # Verify it's callable
        assert callable(tool)
        
        # Check that the tool has the expected name
        assert tool.name == "reddit_search"
    
    def test_search_query_creation(self):
        """Test that SearchQuery and SubmissionFilter models work correctly."""
        filter_obj = SubmissionFilter(
            score=5,
            num_comments=3,
            filter_prompt="Test filter"
        )
        
        query = SearchQuery(
            subreddit="startups",
            query="business ideas",
            sort="top",
            time_filter="month",
            filter=filter_obj
        )
        
        assert query.subreddit == "startups"
        assert query.query == "business ideas"
        assert query.sort == "top"
        assert query.time_filter == "month"
        assert query.filter.score == 5
        assert query.filter.num_comments == 3
    
    def test_reddit_submission_model(self):
        """Test RedditSubmission model validation."""
        submission = RedditSubmission(
            id="test123",
            summary="Test summary",
            comments_summary="Test comments",
            score=10,
            num_comments=5,
            created_utc=datetime.now(),
            upvote_ratio=0.85
        )
        
        assert submission.id == "test123"
        assert submission.score == 10
        assert submission.num_comments == 5
        assert 0 <= submission.upvote_ratio <= 1
        
    def test_reddit_search_tool_parameters(self):
        """Test that the search tool accepts the correct parameters."""
        # Mock dependencies
        mock_reddit = Mock()
        mock_llm = Mock()
        service = RedditToolsService(reddit=mock_reddit, llm=mock_llm)
        
        # Mock the search method to return a valid result
        mock_result = Mock()
        mock_result.subreddit = "startups"
        mock_result.submissions = []
        service.search = Mock(return_value=mock_result)
        
        # Create the tool
        tool = create_reddit_search_tool(service)
        
        # Test calling the tool with all parameters
        result = tool.invoke({
            "subreddit": "startups",
            "query": "AI business",
            "sort": "hot",
            "time_filter": "week",
            "min_score": 5,
            "min_comments": 2,
            "filter_prompt": "Test filter"
        })
        
        # Verify the service.search was called
        service.search.assert_called_once()
        
        # Verify the result
        assert result.subreddit == "startups"