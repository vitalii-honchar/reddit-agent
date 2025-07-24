from uuid import UUID

from sqlmodel import Session, select
from models import AgentConfiguration, AgentExecution
from typing import Sequence


class AgentConfigurationRepository:

    def create(self, session: Session, agent_configuration: AgentConfiguration) -> AgentConfiguration:
        session.add(agent_configuration)
        session.commit()
        session.refresh(agent_configuration)
        return agent_configuration

    def find_all(self, session: Session) -> Sequence[AgentConfiguration]:
        return session.exec(select(AgentConfiguration)).all()

    def get_by_id(self, session: Session, configuration_id: UUID) -> AgentConfiguration:
        return session.exec(
            select(AgentConfiguration).where(AgentConfiguration.id == configuration_id)  # type: ignore
        ).one()


class AgentExecutionRepository:

    def create(self, session: Session, agent_execution: AgentExecution) -> AgentExecution:
        session.add(agent_execution)
        session.commit()
        session.refresh(agent_execution)
        return agent_execution
