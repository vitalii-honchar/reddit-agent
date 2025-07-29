import logging

from core.scheduler import Scheduler
from insights.services import AgentAPIService


class InsightsScheduler(Scheduler):

    def __init__(
            self,
            timeout_seconds: float,
            logger: logging.Logger,
            agent_api_service: AgentAPIService,
    ):
        super().__init__(timeout_seconds, logger)
        self.agent_api_service = agent_api_service

    async def execute(self):
        # self.agent_api_service.
        pass