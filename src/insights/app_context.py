from pydantic_settings import BaseSettings
from sqlmodel import create_engine

from insights.scheduler import InsightsScheduler
from insights.services import AgentAPIService


class AppSettings(BaseSettings):
    db_url: str
    agent_api_base_url: str
    debug: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "INDIE_HACKERS_AGENT_"
        extra = "allow"


class AppContext:

    def __init__(self, settings: AppSettings):
        self.db_engine = create_engine(settings.db_url, echo=settings.debug)
        self.agent_api_service = AgentAPIService(settings.agent_api_base_url)
        self.scheduler = InsightsScheduler(self.agent_api_service)


def create_app_context() -> AppContext:
    return AppContext(AppSettings())  # type: ignore
