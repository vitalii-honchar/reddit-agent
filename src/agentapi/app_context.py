from pydantic_settings import BaseSettings
from sqlmodel import create_engine

from core.repositories import AgentConfigurationRepository, AgentExecutionRepository
from core.services import AgentConfigurationService, AgentExecutionService
from scheduler.scheduler import SchedulerManager
from scheduler.scheduler_app_context import SchedulerAppContext
from scheduler.settings import SchedulerSettings


class AppSettings(BaseSettings):
    db_url: str
    debug: bool = False

    class Config:
        env_file = ".env"
        env_prefix = "INDIE_HACKERS_AGENT_"
        extra = "allow"


class AppContext:

    def __init__(self, settings: AppSettings):
        self.agent_configuration_repository = AgentConfigurationRepository()
        self.agent_execution_repository = AgentExecutionRepository()
        self.agent_configuration_service = AgentConfigurationService(self.agent_configuration_repository)
        self.agent_execution_service = AgentExecutionService(self.agent_execution_repository)
        self.scheduler_settings = SchedulerSettings()  # type: ignore
        self.scheduler_ctx = SchedulerAppContext(self.scheduler_settings)
        self.scheduler_manager = SchedulerManager(
            self.scheduler_settings.poll_interval_seconds,
            self.scheduler_ctx.scheduler_service,
            self.scheduler_ctx.db_engine,
        )
        self.db_engine = create_engine(settings.db_url, echo=settings.debug)


def create_app_context() -> AppContext:
    return AppContext(AppSettings())  # type: ignore
