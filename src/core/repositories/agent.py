from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlmodel import Session, select
from sqlalchemy import and_, or_, func
from core.models import AgentConfiguration, AgentExecution
from typing import Sequence, Optional


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

    def find_pending(self, session: Session, limit: int = 100, cooldown_seconds: int = 600) -> Sequence[AgentExecution]:
        """
        Find pending executions ready for processing.
        
        Returns executions where:
        - state = 'pending' AND 
        - (executions = 0 OR updated_at < NOW() - cooldown_seconds)
        
        Ordered by updated_at ASC for FIFO processing.
        """
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        cooldown_threshold = now - timedelta(seconds=cooldown_seconds)
        
        return session.exec(
            select(AgentExecution)
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

    def try_acquire_lock(self, session: Session, execution_id: UUID, current_executions: int) -> Optional[AgentExecution]:
        """
        Try to acquire optimistic lock on an execution record.
        
        Returns the updated execution if lock was acquired, None if another process got it first.
        Uses the executions counter as an optimistic lock.
        """
        from core.models.agent import utcnow
        
        # Try to increment executions counter atomically
        result = session.exec(
            select(AgentExecution)
            .where(
                and_(
                    AgentExecution.id == execution_id,
                    AgentExecution.executions == current_executions
                )
            )
        ).first()
        
        if result is None:
            # Lock was already acquired by another process
            return None
            
        # Update the execution counter and timestamp
        result.executions = current_executions + 1
        result.updated_at = utcnow()
        session.commit()
        session.refresh(result)
        
        return result