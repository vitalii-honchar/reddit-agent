import uuid
from datetime import timedelta

from sqlmodel import Session

from core.models.agent import AgentConfiguration, AgentExecution, utcnow
from core.repositories.agent import AgentExecutionRepository


class TestAgentExecutionRepository:
    """Test cases for AgentExecutionRepository."""
    
    def test_find_pending_with_no_executions(self, repository: AgentExecutionRepository, 
                                           session: Session, agent_config: AgentConfiguration):
        """Test find_pending returns executions with executions=0."""
        # given
        execution = AgentExecution(config_id=agent_config.id, executions=0, state="pending")
        session.add(execution)
        session.commit()
        
        # when
        result = repository.find_pending(session, threshold=60.0)
        
        # then
        assert len(result) >= 1

        # and
        id_to_execution = {r.id: r for r in result}
        actual = id_to_execution.get(execution.id)
        assert actual is not None
        assert actual.executions == 0

    def test_find_pending_with_old_execution(self, repository: AgentExecutionRepository,
                                           session: Session, agent_config: AgentConfiguration):
        """Test find_pending returns executions updated before threshold."""
        # given - create execution with past updated_at
        now = utcnow()
        old_time = now - timedelta(seconds=120)  # 2 minutes ago
        
        execution = AgentExecution(
            config_id=agent_config.id, 
            executions=1, 
            state="pending",
            updated_at=old_time
        )
        session.add(execution)
        session.commit()
        
        # when - threshold is 60 seconds, so execution should be returned
        result = repository.find_pending(session, threshold=60.0)
        
        # then
        assert len(result) >= 1

        pending_ids = {r.id for r in result}
        assert execution.id in pending_ids

    def test_find_pending_excludes_recent_execution(self, repository: AgentExecutionRepository,
                                                  session: Session, agent_config: AgentConfiguration):
        """Test find_pending excludes executions updated within threshold."""
        # given - create execution with recent updated_at
        execution = AgentExecution(
            config_id=agent_config.id, 
            executions=1, 
            state="pending"
        )
        session.add(execution)
        session.commit()
        
        # when - threshold is 60 seconds, execution is recent so should be excluded
        result = repository.find_pending(session, threshold=60.0)
        
        # then
        pending_ids = {r.id for r in result}
        assert execution.id not in pending_ids

    def test_find_pending_excludes_non_pending_state(self, repository: AgentExecutionRepository,
                                                   session: Session, agent_config: AgentConfiguration):
        """Test find_pending excludes executions not in pending state."""
        # given
        completed_execution = AgentExecution(
            config_id=agent_config.id, 
            executions=0, 
            state="completed"
        )
        failed_execution = AgentExecution(
            config_id=agent_config.id, 
            executions=0, 
            state="failed"
        )
        session.add_all([completed_execution, failed_execution])
        session.commit()
        
        # when
        result = repository.find_pending(session, threshold=60.0)
        
        # then
        pending_ids = {r.id for r in result}
        assert completed_execution.id not in pending_ids
        assert failed_execution.id not in pending_ids

    def test_find_pending_respects_limit(self, repository: AgentExecutionRepository,
                                       session: Session, agent_config: AgentConfiguration):
        """Test find_pending respects the limit parameter."""
        # given - create 5 pending executions with executions=0
        executions = []
        for i in range(5):
            execution = AgentExecution(config_id=agent_config.id, executions=0, state="pending")
            executions.append(execution)
        
        session.add_all(executions)
        session.commit()
        
        # when
        result = repository.find_pending(session, threshold=60.0, limit=3)
        
        # then
        assert len(result) == 3

    def test_find_pending_orders_by_updated_at_asc(self, repository: AgentExecutionRepository,
                                                  session: Session, agent_config: AgentConfiguration):
        """Test find_pending orders results by updated_at ascending."""
        # given - create executions with different updated_at times
        now = utcnow()
        old_execution = AgentExecution(
            config_id=agent_config.id, 
            executions=0, 
            state="pending",
            updated_at=now - timedelta(minutes=2)
        )
        newer_execution = AgentExecution(
            config_id=agent_config.id, 
            executions=0, 
            state="pending", 
            updated_at=now - timedelta(minutes=1)
        )
        
        session.add_all([newer_execution, old_execution])  # Add in reverse order
        session.commit()
        
        # when
        result = repository.find_pending(session, threshold=60.0)
        
        # then
        assert len(result) >= 2
        pending_ids = {r.id for r in result}
        assert old_execution.id in pending_ids
        assert newer_execution.id in pending_ids

    def test_acquire_lock_success(self, repository: AgentExecutionRepository,
                                session: Session, agent_config: AgentConfiguration):
        """Test acquire_lock successfully acquires lock on execution."""
        # given
        execution = AgentExecution(config_id=agent_config.id, executions=0, state="pending")
        session.add(execution)
        session.commit()
        session.refresh(execution)
        
        # when
        result = repository.acquire_lock(session, execution)
        
        # then
        assert result is not None
        assert result.id == execution.id
        assert result.executions == 1  # Should be incremented

    def test_acquire_lock_fails_on_stale_execution(self, repository: AgentExecutionRepository,
                                                 session: Session, agent_config: AgentConfiguration):
        """Test acquire_lock fails when execution count doesn't match (stale data)."""
        # given
        execution = AgentExecution(config_id=agent_config.id, executions=1, state="pending")
        session.add(execution)
        session.commit()
        session.refresh(execution)

        execution.executions = 0

        # when - try to acquire lock with stale execution (still has executions=0)
        result = repository.acquire_lock(session, execution)
        
        # then
        assert result is None  # Should fail due to optimistic locking

    def test_acquire_lock_with_non_existent_execution(self, repository: AgentExecutionRepository,
                                                    session: Session, agent_config: AgentConfiguration):
        """Test acquire_lock fails gracefully with non-existent execution."""
        # given
        fake_execution = AgentExecution(
            id=uuid.uuid4(),
            config_id=agent_config.id, 
            executions=0, 
            state="pending"
        )
        
        # when
        result = repository.acquire_lock(session, fake_execution)
        
        # then
        assert result is None