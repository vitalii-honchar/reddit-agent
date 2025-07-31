import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from insights import routes
from .dependencies import ctx


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ctx.agent_configuration_service.migrate()
    if ctx.settings.scheduler_enabled:
        threading.Thread(
            target=lambda: asyncio.run(ctx.scheduler.start()),
            daemon=True
        ).start()

    yield

    if ctx.settings.scheduler_enabled:
        await ctx.scheduler.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(routes.insights)
