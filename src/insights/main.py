import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from insights import routes
from .dependencies import ctx


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ctx.agent_configuration_service.migrate()

    threading.Thread(
        target=lambda: asyncio.run(ctx.scheduler.start()),
        daemon=True
    ).start()

    yield

    await ctx.scheduler_manager.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(routes.insights)
