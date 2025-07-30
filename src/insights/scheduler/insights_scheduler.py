import logging
import uuid

from core.scheduler import Scheduler
from insights.agentapi_client.fast_api_client.models import AgentExecutionCreate
from insights.services import AgentAPIService, configs


class InsightsScheduler(Scheduler):

    def __init__(
            self,
            timeout_seconds: float,
            logger: logging.Logger,
            base_url: str,
    ):
        super().__init__(timeout_seconds, logger)
        self.base_url = base_url

    async def execute(self):
        self.logger.info("Executing agents: %d", len(configs))
        agent_api_service = AgentAPIService(self.base_url)
        for config in configs:
            self.logger.info("Executing agent: config_id = %s", config.id)
            await agent_api_service.create_execution(
                AgentExecutionCreate(id=uuid.uuid4(), config_id=config.id)
            )

        self.logger.info("Executed agents: %d", len(configs))
