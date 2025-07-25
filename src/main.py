from fastapi import FastAPI
import routes

app = FastAPI()
app.include_router(routes.agents)
app.include_router(routes.agent_configurations)
app.include_router(routes.agent_executions)