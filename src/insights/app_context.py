from pydantic_settings import BaseSettings
from sqlmodel import create_engine

from insights.scheduler import InsightsScheduler
from insights.services import AgentAPIService, AgentConfigurationService
import logging

class AppSettings(BaseSettings):
    db_url: str
    agent_api_base_url: str
    insights_scheduler_timeout: int = 600
    debug: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "INDIE_HACKERS_AGENT_"
        extra = "allow"


class AppContext:

    def __init__(self, settings: AppSettings):
        self.db_engine = create_engine(settings.db_url, echo=settings.debug)
        self.agent_api_service = AgentAPIService(settings.agent_api_base_url)
        self.logger = logging.getLogger("uvicorn")
        self.agent_configuration_service = AgentConfigurationService(self.agent_api_service, self.logger)
        self.scheduler = InsightsScheduler(
            timeout_seconds=settings.insights_scheduler_timeout,
            logger=self.logger,
            base_url=settings.agent_api_base_url,
        )


def create_app_context() -> AppContext:
    return AppContext(AppSettings())  # type: ignore
