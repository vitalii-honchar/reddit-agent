import asyncio
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(routes.insights)
