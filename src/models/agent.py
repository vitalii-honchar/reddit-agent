
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import uuid4, UUID
from datetime import datetime

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

class AgentExecution(SQLModel, table=True):
    __tablename__ = "agent_execution"

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
    config_id: UUID = Field(sa_column=Column(PG_UUID(as_uuid=True), foreign_key="agent_configuration.id"))
    config: AgentConfiguration = Relationship(cascade_delete=True, link_model=AgentConfiguration)



