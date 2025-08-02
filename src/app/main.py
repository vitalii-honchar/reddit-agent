"""
Modular monolith main application entry point.

This application combines the previously separate microservices:
- AgentAPI: REST API for agent configuration and execution management
- Insights: Web-based frontend with dashboard and scheduling  
- Scheduler: Background service for automated agent execution

Each module is configured independently using the AppModule pattern for loose coupling.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from agentapi.module import AgentAPIModule
from insights.module import InsightsModule
from scheduler.module import SchedulerModule
from scheduler.settings import SchedulerConfig


def create_app() -> FastAPI:
    modules = [
        InsightsModule(),
        AgentAPIModule(),
        SchedulerModule(),
    ]

    # Define lifespan manager
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        for module in modules:
            await module.on_startup()

        yield

        for module in modules:
            await module.on_shutdown()

    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Reddit Agent Platform",
        description="Comprehensive platform for Reddit business opportunity agents",
        version="1.0.0",
        lifespan=lifespan
    )

    for module in modules:
        module.init(app)

    return app


app = create_app()
