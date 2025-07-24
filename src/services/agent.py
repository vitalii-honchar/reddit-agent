from dataclasses import dataclass
from sqlmodel import Session

from models import AgentConfiguration
from repositories import AgentConfigurationRepository
from typing import Sequence

from schemas import AgentConfigurationCreate
from uuid import UUID


@dataclass
class AgentConfigurationService:
    repository: AgentConfigurationRepository

    def create(self, session: Session, create: AgentConfigurationCreate) -> AgentConfiguration:
        return self.repository.create(session, AgentConfiguration.model_validate(create))

    def find_all(self, session: Session) -> Sequence[AgentConfiguration]:
        return self.repository.find_all(session)

    def get_by_id(self, session: Session, configuration_id: UUID) -> AgentConfiguration:
        return self.repository.get_by_id(session, configuration_id)