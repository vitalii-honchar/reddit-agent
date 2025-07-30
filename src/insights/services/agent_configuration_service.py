import logging
import uuid

from insights.agentapi_client.fast_api_client.models import AgentConfigurationUpdate, AgentConfigurationUpdateData
from insights.services import AgentAPIService
from logging import Logger

configs = [
    AgentConfigurationUpdate(
        id=uuid.UUID("1b676236-6d21-11f0-9248-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching SaaS product launch strategies and growth tactics.
                Focus on:
                - Successful SaaS product launch case studies
                - Customer acquisition strategies for B2B SaaS
                - Pricing strategies and revenue model discussions
                - Product-market fit validation techniques
                - Growth hacking tactics specific to SaaS companies

                Strict restrictions:
                - Only include posts with at least 20 upvotes and 10 comments
                - Focus on proven strategies with measurable results
                - Prioritize posts from experienced SaaS founders
                - Exclude generic marketing advice not SaaS-specific
                - Look for posts with concrete metrics and outcomes""",
            "search_query": "SaaS product launch strategies customer acquisition growth",
            "search_types": ["reddit"],
        }),
    )
]


class AgentConfigurationService:

    def __init__(self, agent_api_service: AgentAPIService, logger: Logger):
        self.agent_api_service = agent_api_service
        self.logger = logger

    async def migrate(self):
        self.logger.info("Migrating agent configurations: %d", len(configs))
        for config in configs:
            logging.info("Migrating agent configuration: %s", config.id)
            res = await self.agent_api_service.upsert_configuration(config)
            if not res:
                raise RuntimeError(f"Failed to upsert configuration: {config.id}")

        self.logger.info("Migrated agent configurations: %d", len(configs))
