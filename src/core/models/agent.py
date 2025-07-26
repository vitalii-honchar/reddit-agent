from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, INTEGER as PG_INTEGER, JSONB
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Dict, Any, Literal, get_args, Optional

AgentType = Literal["search_agent"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AgentConfiguration(SQLModel, table=True):
    __tablename__ = "agent_configuration"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    agent_type: AgentType = Field(
        sa_column=Column(Enum(*get_args(AgentType), name="agent_type_enum"), nullable=False)
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    )
    data: Dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=True)
    )


AgentExecutionState = Literal["pending", "completed", "failed"]


class AgentExecution(SQLModel, table=True):
    __tablename__ = "agent_execution"
    __table_args__ = (
        Index("ix_agent_execution_pending_updated_at", "updated_at",
              postgresql_where=Column("state") == "pending"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    state: AgentExecutionState = Field(
        default="pending",
        sa_column=Column(Enum(*get_args(AgentExecutionState), name="agent_execution_state"), nullable=False,
                         default="pending")
    )
    executions: int = Field(default=0, sa_column=Column(PG_INTEGER, nullable=False, default=0))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    )
    config_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("agent_configuration.id")))
    success_result: Dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    error_result: Dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    config: AgentConfiguration = Relationship()
