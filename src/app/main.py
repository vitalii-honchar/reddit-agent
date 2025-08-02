"""
Modular monolith main application entry point.

This application combines the previously separate microservices:
- AgentAPI: REST API for agent configuration and execution management
- Insights: Web-based frontend with dashboard and scheduling  
- Scheduler: Background service for automated agent execution

Each module is configured independently using the AppModule pattern for loose coupling.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI

from insights.module import InsightsModule
from insights.settings import InsightsConfig
from agentapi.module import AgentAPIModule  
from agentapi.settings import AgentAPIConfig
from scheduler.module import SchedulerModule
from scheduler.settings import SchedulerConfig


def create_app() -> FastAPI:
    """Create and configure the FastAPI application with all modules"""
    
    # Initialize configuration
    insights_config = InsightsConfig()
    agentapi_config = AgentAPIConfig()
    scheduler_config = SchedulerConfig()
    
    # Initialize modules
    insights_module = InsightsModule(insights_config)
    agentapi_module = AgentAPIModule(agentapi_config, scheduler_config)
    scheduler_module = SchedulerModule(scheduler_config)
    
    # Store modules for lifespan access
    modules = [insights_module, agentapi_module, scheduler_module]
    
    # Define lifespan manager
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: call on_startup for all modules
        for module in modules:
            await module.on_startup()
        
        yield
        
        # Shutdown: call on_shutdown for all modules
        for module in modules:
            await module.on_shutdown()
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Reddit Agent Platform",
        description="Comprehensive platform for Reddit business opportunity agents",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Configure each module with the app
    for module in modules:
        module.init(app)
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "src.app.main:app",
        host=host,
        port=port,
        reload=True
    )