from fastapi import APIRouter
from uuid import UUID
from agentapi.schemas import AgentExecutionCreate, AgentExecutionRead
from agentapi.dependencies import SessionDep, AgentExecutionServiceDep

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
