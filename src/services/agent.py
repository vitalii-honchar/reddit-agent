from dataclasses import dataclass
from sqlmodel import Session

from models import AgentConfiguration, AgentExecution
from repositories import AgentConfigurationRepository, AgentExecutionRepository
from typing import Sequence

from schemas import AgentConfigurationCreate
from uuid import UUID

from schemas.agent_execution import AgentExecutionCreate


@dataclass
class AgentConfigurationService:
    repository: AgentConfigurationRepository

    def create(self, session: Session, create: AgentConfigurationCreate) -> AgentConfiguration:
        return self.repository.create(session, AgentConfiguration.model_validate(create))

    def find_all(self, session: Session) -> Sequence[AgentConfiguration]:
        return self.repository.find_all(session)

    def get_by_id(self, session: Session, configuration_id: UUID) -> AgentConfiguration:
        return self.repository.get_by_id(session, configuration_id)

@dataclass
class AgentExecutionService:
    repository: AgentExecutionRepository

    def create(self, session: Session, create: AgentExecutionCreate) -> AgentExecution:
        return self.repository.create(session, AgentExecution.model_validate(create))

    def find_all(self, session: Session) -> Sequence[AgentExecution]:
        return self.repository.find_all(session)

    def get_by_id(self, session: Session, configuration_id: UUID) -> AgentExecution:
        return self.repository.get_by_id(session, configuration_id)