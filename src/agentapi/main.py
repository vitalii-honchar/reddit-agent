import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI

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