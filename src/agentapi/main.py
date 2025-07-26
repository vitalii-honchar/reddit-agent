from fastapi import FastAPI
from agentapi import routes

app = FastAPI()
app.include_router(routes.agent_configurations)
app.include_router(routes.agent_executions)