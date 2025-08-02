from datetime import timedelta
from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlmodel import Session, select, update
from sqlalchemy.exc import NoResultFound

from core.models import AgentConfiguration, AgentExecution, utcnow, AgentExecutionState


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

    def upsert(self, session: Session, agent_configuration: AgentConfiguration) -> AgentConfiguration:
        """Create or update an agent configuration. If ID exists, update; otherwise, create."""
        try:
            # Try to get existing configuration
            existing = session.exec(
                select(AgentConfiguration).where(AgentConfiguration.id == agent_configuration.id)  # type: ignore
            ).one()

            # Update existing configuration
            existing.agent_type = agent_configuration.agent_type
            existing.data = agent_configuration.data
            existing.updated_at = utcnow()

            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        except NoResultFound:
            # Configuration doesn't exist, create new one
            return self.create(session, agent_configuration)


class AgentExecutionRepository:

    def create(self, session: Session, agent_execution: AgentExecution) -> AgentExecution:
        session.add(agent_execution)
        session.commit()
        session.refresh(agent_execution)
        return agent_execution

    def find_all(self, session: Session) -> Sequence[AgentExecution]:
        return session.exec(select(AgentExecution)).all()

    def get_by_id(self, session: Session, execution_id: UUID) -> AgentExecution:
        return session.exec(
            select(AgentExecution).where(AgentExecution.id == execution_id)  # type: ignore
        ).one()

    def update(self, session: Session, agent_execution: AgentExecution) -> AgentExecution:
        """Generic update method using SQLModel instance"""
        session.add(agent_execution)
        session.commit()
        session.refresh(agent_execution)
        return agent_execution

    def find_pending(self, session: Session, threshold: float, limit: int = 100) -> Sequence[AgentExecution]:
        now = utcnow()
        cooldown_threshold = now - timedelta(seconds=threshold)

        return session.exec(
            select(AgentExecution)  # type: ignore
            .where(
                and_(
                    AgentExecution.state == "pending",
                    or_(
                        AgentExecution.executions == 0,
                        AgentExecution.updated_at < cooldown_threshold
                    )
                )
            )
            .order_by(AgentExecution.updated_at.asc())  # type: ignore
            .limit(limit)
        ).all()

    def acquire_lock(self, session: Session, execution: AgentExecution) -> AgentExecution | None:
        with Session(session.get_bind()) as lock_session:
            with lock_session.connection(execution_options={"isolation_level": "AUTOCOMMIT"}) as connection:
                res = connection.execute(
                    update(AgentExecution).where(  # type: ignore
                        and_(
                            AgentExecution.id == execution.id,
                            AgentExecution.executions == execution.executions
                        )
                    ).values(executions=execution.executions + 1)
                )

                if res.rowcount > 0:  # type: ignore
                    session.refresh(execution)
                    return execution

        return None

    def get_recent(
            self,
            session: Session,
            config: AgentConfiguration,
            state: AgentExecutionState,
            limit: int = 10
    ) -> Sequence[AgentExecution]:
        conditions = [
            and_(
                AgentExecution.config_id == config.id,
                AgentExecution.state == state
            )
        ]

        if config.agent_type == "search_agent":
            conditions.append(
                func.jsonb_array_length(
                    AgentExecution.success_result['findings']
                ) > 0
            )

        query = (select(AgentExecution).where(*conditions)
                 .order_by(AgentExecution.updated_at.desc()).limit(limit))  # type: ignore

        return session.exec(query).all()  # type: ignore
