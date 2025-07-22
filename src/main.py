"""Main script to run search agent with configuration from environment variables."""
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from praw import Reddit
from langchain_openai import ChatOpenAI

from config import Config
from config.config import RedditConfig
from search_agent.models import CreateSearchAgentCommand
from search_agent.search_agent import execute_search

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file."""
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
    else:
        load_dotenv()
        logger.info("Loaded environment from current directory")

def create_config() -> Config:
    """Create configuration from environment variables."""
    # Reddit configuration
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")
    
    if not all([client_id, client_secret, user_agent]):
        raise ValueError("Reddit API credentials not configured. Please set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT in .env file")
    
    reddit_config = RedditConfig(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    
    # OpenAI configuration
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
    
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        api_key=api_key
    )
    
    return Config(llm=llm, reddit_config=reddit_config)

def main():
    """Main function to execute search agent."""
    logger.info("Starting search agent...")
    
    # Load environment variables
    load_environment()
    
    # Create configuration
    config = create_config()
    logger.info("Configuration created successfully")
    
    # Create search command (same as in test)
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
    
    logger.info(f"Executing search with query: {command.search_query}")
    
    # Execute search
    result = execute_search(config, command)
    
    # Log results
    logger.info(f"Search completed. Found {len(result.reddit_search_results)} search results:")
    logger.info(result.model_dump_json(indent=2))

if __name__ == "__main__":
    main()