from fastapi import APIRouter, Query
from uuid import UUID
from agentapi.schemas import AgentExecutionCreate, AgentExecutionRead
from agentapi.dependencies import SessionDep, AgentExecutionServiceDep
from typing import List
from core.models import AgentExecutionState

router = APIRouter(prefix="/agent-executions", tags=["agent-executions"])


@router.post("/")
def create_execution(
        session: SessionDep,
        execution_svc: AgentExecutionServiceDep,
        execution_create: AgentExecutionCreate
) -> UUID:
    res = execution_svc.create(session, execution_create)
    return res.id


@router.get("/{execution_id}", response_model=AgentExecutionRead)
def get_execution(
        session: SessionDep,
        execution_svc: AgentExecutionServiceDep,
        execution_id: UUID
):
    return execution_svc.get_by_id(session, execution_id)


@router.get("/", response_model=List[AgentExecutionRead])
def get_recent_executions(
        session: SessionDep,
        execution_svc: AgentExecutionServiceDep,
        limit: int = Query(10, description="Maximum number of results to return"),
        config_id: UUID = Query(..., description="Filter by configuration ID"),
        state: AgentExecutionState = Query(..., description="Filter by execution state")
):
    return execution_svc.get_recent(session, config_id=config_id, state=state, limit=limit)
