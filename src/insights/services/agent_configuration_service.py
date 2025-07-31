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
               - Successful SaaS product launch case studies with revenue numbers
               - First 100 customers acquisition playbooks for B2B SaaS
               - Pricing model pivots that doubled revenue
               - Product-market fit signals (NPS >50, <2% monthly churn)
               - Zero to $10K MRR growth tactics with exact steps

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must mention specific metrics (MRR, CAC, LTV, conversion rates)
               - Prioritize posts from founders who reached $100K+ ARR
               - Exclude vague "build great product" bullshit advice
               - Look for tactical breakdowns, not motivational fluff""",
            "search_query": "SaaS product launch strategies customer acquisition growth",
            "search_types": ["reddit"],
        }),
    ),
    AgentConfigurationUpdate(
        id=uuid.UUID("1f866f9a-6de6-11f0-9cdb-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching cybersecurity startup launches by indie hackers and small teams.
               Focus on:
               - Security tools/services launched with <5 person teams
               - B2B cybersecurity products hitting first $10K MRR
               - Compliance/certification hacks for bootstrapped security startups
               - Customer trust building without enterprise backing
               - Security audit tools, pen-testing services, vulnerability scanners by indies

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must be actual security products (not just privacy-focused apps)
               - Founder must share revenue/user numbers or acquisition story
               - Exclude enterprise vendors or VC-backed companies
               - Look for bootstrap-friendly niches (SMB security, developer tools)""",
            "search_query": "cybersecurity startup indie hacker security tool launch bootstrap",
            "search_types": ["reddit"],
        }),
    ),
    AgentConfigurationUpdate(
        id=uuid.UUID("2a64ea22-6de6-11f0-9bbe-5ee52574761b"),
        agent_type="search_agent",
        data=AgentConfigurationUpdateData.from_dict({
            "behavior": """You are researching idea validation and product launch tactics used by indie hackers.
               Focus on:
               - Pre-launch validation that predicted >$5K MRR success
               - Failed ideas and exactly why they died (with numbers)
               - Landing page conversion experiments with A/B test results
               - Product Hunt launch postmortems with traffic/conversion data
               - Reddit/Twitter/community launch strategies that generated >100 paying users

               Strict restrictions:
               - Only include posts with at least 20 upvotes and 10 comments
               - Must include specific validation metrics (survey responses, pre-orders, waitlist conversions)
               - Prioritize posts with "here's what didn't work" sections
               - Exclude "I built this in a weekend" humble brags without data
               - Look for step-by-step launch sequences with timestamps""",
            "search_query": "indie hacker idea validation product launch marketing tactics failed",
            "search_types": ["reddit"],
        }),
    ),
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
