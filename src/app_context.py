from pathlib import Path

from pydantic_settings import BaseSettings
from langchain_openai import ChatOpenAI
import asyncpraw

from ai.prompt.prompt_manager import PromptManager
from ai.search_agent.tool.reddit.tools import RedditToolsService


class AppSettings(BaseSettings):
    reddit_client_id: str
    reddit_client_secret: str
    reddit_agent: str
    openai_api_key: str
    llm_model: str = 'gpt-4.1'
    llm_model_temperature: float = 0.1
    prompts_folder: str

    class Config:
        env_file = ".env"
        env_prefix = "INDIE_HACKERS_AGENT_"

class AppContext:

    def __init__(self, settings: AppSettings):
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_model_temperature,
            api_key=settings.openai_api_key,
        )
        self.prompt_manager = PromptManager(Path(settings.prompts_folder))
        self.reddit_tools_service = RedditToolsService(
            asyncpraw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                user_agent=settings.reddit_agent,
            )
        )