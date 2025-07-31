import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from agentapi import routes
from .dependencies import ctx


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler_thread = threading.Thread(
        target=lambda: asyncio.run(ctx.scheduler_manager.start()),
        daemon=True
    )
    scheduler_thread.start()
    
    yield
    
    ctx.scheduler_manager.shutdown_event.set()


app = FastAPI(lifespan=lifespan)
app.include_router(routes.agent_configurations)
app.include_router(routes.agent_executions)

# Setup templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """Main dashboard page showing recent execution results."""
    # Get recent executions
    async with ctx.session_factory() as session:
        recent_executions = ctx.agent_execution_service.get_recent(session, limit=10)
    
    return templates.TemplateResponse(
        "main.html", 
        {"request": request, "executions": recent_executions}
    )