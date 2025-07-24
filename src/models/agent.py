
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, INTEGER as PG_INTEGER, JSONB
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, Any

class AgentConfiguration(SQLModel, table=True):
    __tablename__ = "agent_configuration"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
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
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now(), nullable=False)
    )
    config_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), ForeignKey("agent_configuration.id")))
    config: AgentConfiguration = Relationship(cascade_delete=True, link_model=AgentConfiguration)



