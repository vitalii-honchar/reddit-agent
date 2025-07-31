from typing import Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from insights.services import AgentAPIService, configs

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
            state="completed",
            limit=10
        )
    except Exception as e:
        logger.exception(f"Failed to fetch executions for config {config_id}")
        executions = []
    
    return templates.TemplateResponse(
        "insights/main.html",
        {
            "request": request,
            "executions": executions,
            "configs": configs,
            "selected_config": config_id
        }
    )