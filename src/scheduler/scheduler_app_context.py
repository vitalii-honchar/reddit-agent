from core.repositories import AgentExecutionRepository, AgentConfigurationRepository
from core.services import AgentExecutionService
from scheduler.services import AgentExecutor, SchedulerService
from scheduler.settings import SchedulerSettings
from sqlmodel import create_engine

class SchedulerAppContext:

    def __init__(self, settings: SchedulerSettings):
        self.settings = settings
        self.agent_executor = AgentExecutor(self.settings)
        self.agent_execution_repository = AgentExecutionRepository()
        self.agent_configuration_repository = AgentConfigurationRepository()
        self.agent_execution_service = AgentExecutionService(self.agent_execution_repository)
        self.scheduler_service = SchedulerService(
            execution_service=self.agent_execution_service,
            executor=self.agent_executor,
            settings=self.settings,
        )
        self.db_engine = create_engine(settings.db_url, echo=settings.debug)