from fastapi import FastAPI
import routes

app = FastAPI()
app.include_router(routes.agents)
