from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Any


class AgentExecutionCreate(BaseModel):
    id: UUID = Field(description="Agent ID")
    config_id: UUID = Field(description="Agent configuration ID")


class AgentExecutionRead(BaseModel):
    id: UUID = Field(description="Agent ID")
    config_id: UUID = Field(description="Agent configuration ID")
    executions: int = Field(description="Agent executions")
    created_at: datetime = Field(description="Agent execution creation time")
    updated_at: datetime = Field(description="Agent execution update time")
    success_result: Dict[str, Any] | None = Field(description="Success result")
    error_result: Dict[str, Any] | None = Field(description="Error result")