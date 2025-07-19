"""Integration test for Reddit search tool using GPT-4.1"""
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
from praw import Reddit
from langchain_openai import ChatOpenAI
from reddit_agent.tool.reddit.tools import RedditToolsService, create_reddit_search_tool


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
        model="gpt-4o",  # Using gpt-4o as the latest available model
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
        result = reddit_search_tool(
            subreddit="startups",
            query="digital marketing SEO content",
            sort="top",
            time_filter="month",
            min_score=5,
            min_comments=3,
            filter_prompt="""Include posts that discuss:
            - Digital marketing business opportunities
            - SEO consulting or content creation services
            - Online marketing strategies for startups
            - Content marketing and copywriting services
            Exclude posts about unrelated topics or spam."""
        )
        
        # Validate the result structure
        assert result.subreddit == "startups"
        assert isinstance(result.submissions, list)
        
        # Check that we found some relevant submissions
        if result.submissions:
            submission = result.submissions[0]
            assert hasattr(submission, 'id')
            assert hasattr(submission, 'summary')
            assert hasattr(submission, 'score')
            assert submission.score >= 5
            
    def test_search_ai_startup_ideas(self, reddit_search_tool):
        """Test searching for AI-related startup opportunities."""
        result = reddit_search_tool(
            subreddit="startups",
            query="AI artificial intelligence business",
            sort="hot",
            time_filter="week",
            min_score=3,
            min_comments=2,
            filter_prompt="""Include posts that discuss:
            - AI-powered business ideas or startups
            - Artificial intelligence applications in business
            - Machine learning opportunities
            - AI consulting or development services
            Exclude generic AI news or theoretical discussions."""
        )
        
        # Validate the result structure
        assert result.subreddit == "startups"
        assert isinstance(result.submissions, list)
        
        # Check submission quality if any found
        for submission in result.submissions:
            assert submission.score >= 3
            assert len(submission.summary) > 0
            assert len(submission.comments_summary) > 0
            
    def test_search_online_education_opportunities(self, reddit_search_tool):
        """Test searching for online education and tutoring business ideas."""
        result = reddit_search_tool(
            subreddit="startups",
            query="online education tutoring course",
            sort="relevance",
            time_filter="month",
            min_score=2,
            min_comments=1,
            filter_prompt="""Include posts that discuss:
            - Online education platform ideas
            - Tutoring and teaching service opportunities
            - Course creation and educational content
            - EdTech startup concepts
            Exclude posts about personal learning experiences."""
        )
        
        # Validate the result structure
        assert result.subreddit == "startups"
        assert isinstance(result.submissions, list)
        
    def test_search_saas_business_ideas(self, reddit_search_tool):
        """Test searching for SaaS business opportunities."""
        result = reddit_search_tool(
            subreddit="startups",
            query="SaaS software service platform",
            sort="top",
            time_filter="month",
            min_score=5,
            min_comments=3,
            filter_prompt="""Include posts that discuss:
            - SaaS business ideas and opportunities
            - Software-as-a-Service platforms
            - B2B software solutions
            - Subscription-based business models
            Exclude posts about using existing SaaS tools."""
        )
        
        # Validate the result structure
        assert result.subreddit == "startups"
        assert isinstance(result.submissions, list)
        
        # Ensure all submissions meet minimum criteria
        for submission in result.submissions:
            assert submission.score >= 5
            
    def test_search_returns_valid_data_structure(self, reddit_search_tool):
        """Test that the search tool returns properly structured data."""
        result = reddit_search_tool(
            subreddit="entrepreneur",  # Using a different subreddit for variety
            query="business opportunity",
            sort="new",
            time_filter="day",
            min_score=1,
            min_comments=1,
            filter_prompt="Include any business-related posts."
        )
        
        # Validate SearchResult structure
        assert hasattr(result, 'subreddit')
        assert hasattr(result, 'submissions')
        assert result.subreddit == "entrepreneur"
        assert isinstance(result.submissions, list)
        
        # Validate RedditSubmission structure if any found
        for submission in result.submissions:
            required_fields = ['id', 'summary', 'comments_summary', 'score', 
                             'num_comments', 'created_utc', 'upvote_ratio']
            for field in required_fields:
                assert hasattr(submission, field), f"Missing field: {field}"