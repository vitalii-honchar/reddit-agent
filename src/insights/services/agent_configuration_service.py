from insights.services import AgentAPIService



class AgentConfigurationService:

    def __init__(self, agent_api_service: AgentAPIService):
        self.agent_api_service = agent_api_service

    async def migrate(self):
        pass