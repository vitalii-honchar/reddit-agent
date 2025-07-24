from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, INTEGER as PG_INTEGER, JSONB
from uuid import uuid4, UUID
from datetime import datetime, timezone
from typing import Dict, Any, Literal, get_args

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


class AgentExecution(SQLModel, table=True):
    __tablename__ = "agent_execution"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    executions: int = Field(sa_column=Column(PG_INTEGER, nullable=False, default=0))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    )
    config_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("agent_configuration.id")))
    config: AgentConfiguration = Relationship()
