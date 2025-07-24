from sqlmodel import create_engine
from pathlib import Path

from pydantic_settings import BaseSettings
from langchain_openai import ChatOpenAI
import asyncpraw

from ai.prompt import PromptManager
from ai.search_agent.tool.reddit.tools import RedditToolsService
from repositories import AgentConfigurationRepository, AgentExecutionRepository
from services import AgentConfigurationService


class AppSettings(BaseSettings):
    reddit_client_id: str
    reddit_client_secret: str
    reddit_agent: str
    openai_api_key: str
    llm_model: str = 'gpt-4.1'
    llm_model_temperature: float = 0.1
    prompts_folder: str = 'prompts'
    db_url: str
    debug: bool = False

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
        self.agent_configuration_repository = AgentConfigurationRepository()
        self.agent_execution_repository = AgentExecutionRepository()
        self.agent_configuration_service = AgentConfigurationService(self.agent_configuration_repository)
        self.db_engine = create_engine(settings.db_url, echo=settings.debug)

def create_app_context() -> AppContext:
    return AppContext(AppSettings())  # type: ignore
