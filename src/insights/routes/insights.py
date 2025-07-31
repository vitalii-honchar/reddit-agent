from typing import Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from insights.services import AgentAPIService, configs
from insights.agentapi_client.fast_api_client.models import GetRecentExecutionsAgentExecutionsGetState

def get_agent_display_name(config):
    """Generate display name based on config ID."""
    config_id = str(config.id)
    if config_id == "1b676236-6d21-11f0-9248-5ee52574761b":
        return "SaaS Launch"
    elif config_id == "1f866f9a-6de6-11f0-9cdb-5ee52574761b":
        return "Cybersecurity"
    elif config_id == "2a64ea22-6de6-11f0-9bbe-5ee52574761b":
        return "Idea Validation"
    else:
        return "Research Agent"

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def insights_page(
    request: Request,
    config_id: Optional[UUID] = Query(None, description="Configuration ID to filter by")
):
    """Insights dashboard page showing search results from agents."""
    # Use first config if none provided
    if config_id is None and configs:
        config_id = configs[0].id
    
    if not config_id:
        # No configs available
        return templates.TemplateResponse(
            "insights/main.html",
            {"request": request, "executions": [], "configs": [], "selected_config": None}
        )
    
    # Get recent completed executions for the config
    agent_api = AgentAPIService()
    try:
        executions = await agent_api.get_recent_executions(
            config_id=config_id,
            state=GetRecentExecutionsAgentExecutionsGetState.COMPLETED,
            limit=10
        )
    except Exception as e:
        logger.exception(f"Failed to fetch executions for config {config_id}")
        executions = []
    
    # Create configs with display names
    configs_with_names = [
        {
            "id": config.id,
            "name": get_agent_display_name(config),
            "config": config
        }
        for config in configs
    ]
    
    return templates.TemplateResponse(
        "insights/main.html",
        {
            "request": request,
            "executions": executions,
            "configs": configs_with_names,
            "selected_config": config_id
        }
    )