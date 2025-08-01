from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, text

from agentapi.dependencies import ctx

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint that verifies database connectivity.
    Returns service status and database connectivity information.
    """
    status = "healthy"
    checks = {}
    
    # Database connectivity check
    try:
        with Session(ctx.db_engine) as session:
            # Simple database ping
            result = session.exec(text("SELECT 1")).first()
            if result == 1:
                checks["database"] = {
                    "status": "healthy",
                    "message": "Database connection successful"
                }
            else:
                checks["database"] = {
                    "status": "unhealthy", 
                    "message": "Database query returned unexpected result"
                }
                status = "unhealthy"
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        status = "unhealthy"
    
    # Scheduler status check
    try:
        if ctx.scheduler_manager.shutdown_event.is_set():
            checks["scheduler"] = {
                "status": "unhealthy",
                "message": "Scheduler is shut down"
            }
            status = "unhealthy"
        else:
            checks["scheduler"] = {
                "status": "healthy",
                "message": "Scheduler is running"
            }
    except Exception as e:
        checks["scheduler"] = {
            "status": "unknown",
            "message": f"Scheduler status check failed: {str(e)}"
        }
    
    response = {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "agentapi",
        "checks": checks
    }
    
    # Return HTTP 503 if unhealthy
    if status == "unhealthy":
        raise HTTPException(status_code=503, detail=response)
    
    return response


