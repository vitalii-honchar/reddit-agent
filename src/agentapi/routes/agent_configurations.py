from fastapi import APIRouter
from uuid import UUID
from agentapi.schemas import AgentConfigurationCreate, AgentConfigurationRead
from dependencies import SessionDep, AgentConfigurationServiceDep
from typing import List

router = APIRouter(prefix="/agent-configurations", tags=["agent-configurations"])


@router.post("/")
def create_configuration(
        session: SessionDep,
        configuration_service: AgentConfigurationServiceDep,
        configuration_create: AgentConfigurationCreate
) -> UUID:
    res = configuration_service.create(session, configuration_create)
    return res.id


@router.get("/{configuration_id}", response_model=AgentConfigurationRead)
def get_configuration(
        session: SessionDep,
        configuration_service: AgentConfigurationServiceDep,
        configuration_id: UUID
):
    return configuration_service.get_by_id(session, configuration_id)

@router.get("/", response_model=List[AgentConfigurationRead])
def get_configurations(session: SessionDep, configuration_service: AgentConfigurationServiceDep):
    return configuration_service.find_all(session)
