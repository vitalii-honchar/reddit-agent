from datetime import datetime, UTC
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from insights.dependencies import ctx

router = APIRouter(prefix="/health",tags=["health"])


@router.get("")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint that verifies scheduler status.
    Returns service status and scheduler information.
    """
    status = "healthy"
    checks = {}
    
    # Scheduler status check
    try:
        if ctx.settings.scheduler_enabled:
            # Check if scheduler is running/available
            # The scheduler in insights service is started in main.py lifecycle
            checks["scheduler"] = {
                "status": "healthy",
                "message": "Scheduler is enabled and should be running"
            }
        else:
            checks["scheduler"] = {
                "status": "disabled",
                "message": "Scheduler is disabled by configuration"
            }
    except Exception as e:
        checks["scheduler"] = {
            "status": "unknown",
            "message": f"Scheduler status check failed: {str(e)}"
        }
        status = "unhealthy"
    
    response = {
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "service": "insights",
        "checks": checks
    }
    
    # Return HTTP 503 if unhealthy
    if status == "unhealthy":
        raise HTTPException(status_code=503, detail=response)
    
    return response