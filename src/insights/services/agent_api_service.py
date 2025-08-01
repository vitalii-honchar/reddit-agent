"""Service for interacting with AgentAPI using generated HTTP client."""

from typing import List, Optional
from uuid import UUID

from insights.agentapi_client.fast_api_client.client import Client
from insights.agentapi_client.fast_api_client.api.agent_configurations import (
    create_configuration_agent_configurations_post,
    get_configuration_agent_configurations_configuration_id_get,
    get_configurations_agent_configurations_get,
    upsert_configuration_agent_configurations_upsert_put,
)
from insights.agentapi_client.fast_api_client.api.agent_executions import (
    create_execution_agent_executions_post,
    get_execution_agent_executions_execution_id_get,
    get_recent_executions_agent_executions_get,
)
from insights.agentapi_client.fast_api_client.models import (
    AgentConfigurationCreate,
    AgentConfigurationRead,
    AgentExecutionCreate,
    AgentExecutionRead, 
    AgentConfigurationUpdate,
    GetRecentExecutionsAgentExecutionsGetState,
)

class AgentAPIService:
    """Async service for interacting with AgentAPI endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the service with async API client.
        
        Args:
            base_url: Base URL for the AgentAPI service
        """
        self.client = Client(base_url=base_url)
    
    # Agent Configuration methods
    
    async def create_configuration(self, config: AgentConfigurationCreate) -> UUID:
        """Create a new agent configuration.
        
        Args:
            config: Configuration data to create
            
        Returns:
            UUID of the created configuration
        """
        response = await create_configuration_agent_configurations_post.asyncio(
            client=self.client,
            body=config
        )
        return UUID(response)
    
    async def get_configuration(self, config_id: UUID) -> Optional[AgentConfigurationRead]:
        """Get an agent configuration by ID.
        
        Args:
            config_id: ID of the configuration to retrieve
            
        Returns:
            Configuration data or None if not found
        """
        return await get_configuration_agent_configurations_configuration_id_get.asyncio(
            client=self.client,
            configuration_id=config_id
        )

    async def upsert_configuration(self, config: AgentConfigurationUpdate) -> Optional[AgentConfigurationRead]:
        return await upsert_configuration_agent_configurations_upsert_put.asyncio(
            client=self.client,
            body=config,
        )
    
    async def get_all_configurations(self) -> List[AgentConfigurationRead]:
        """Get all agent configurations.
        
        Returns:
            List of all configurations
        """
        return await get_configurations_agent_configurations_get.asyncio(
            client=self.client
        )
    
    # Agent Execution methods
    
    async def create_execution(self, execution: AgentExecutionCreate) -> UUID:
        """Create a new agent execution.
        
        Args:
            execution: Execution data to create
            
        Returns:
            UUID of the created execution
        """
        return await create_execution_agent_executions_post.asyncio(
            client=self.client,
            body=execution
        )
    
    async def get_execution(self, execution_id: UUID) -> Optional[AgentExecutionRead]:
        """Get an agent execution by ID.
        
        Args:
            execution_id: ID of the execution to retrieve
            
        Returns:
            Execution data or None if not found
        """
        return await get_execution_agent_executions_execution_id_get.asyncio(
            client=self.client,
            execution_id=execution_id
        )
    
    async def get_recent_executions(
        self, 
        config_id: UUID, 
        state: GetRecentExecutionsAgentExecutionsGetState,
        limit: int = 10
    ) -> List[AgentExecutionRead]:
        """Get recent agent executions for a specific config and state.
        
        Args:
            config_id: Configuration ID to filter by
            state: Execution state to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of recent executions
        """
        return await get_recent_executions_agent_executions_get.asyncio(
            client=self.client,
            config_id=config_id,
            state=state,
            limit=limit
        )