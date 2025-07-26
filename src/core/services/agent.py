from dataclasses import dataclass
from sqlmodel import Session

from core.models import AgentConfiguration, AgentExecution
from core.repositories import AgentConfigurationRepository, AgentExecutionRepository
from typing import Sequence

from agentapi.schemas import AgentConfigurationCreate
from uuid import UUID

from agentapi.schemas.agent_execution import AgentExecutionCreate


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

    def find_pending(self, session: Session, threshold: float, limit: int = 100) -> Sequence[AgentExecution]:
        return self.repository.find_pending(session, threshold, limit)

    def acquire_lock(self, session: Session, execution: AgentExecution) -> AgentExecution | None:
        return self.repository.acquire_lock(session, execution)

    def update(self, session: Session, execution: AgentExecution) -> AgentExecution:
        return self.repository.update(session, execution)