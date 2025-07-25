from datetime import datetime

from pydantic import BaseModel, Field
from uuid import UUID
from typing import Dict, Any
from models import AgentType


class Agent(BaseModel):
    id: UUID = Field(description="Agent ID")
    name: str = Field(description="Agent name")
    description: str = Field(description="Agent description")


class AgentConfigurationCreate(BaseModel):
    agent_type: AgentType = Field(description="Agent type")
    data: Dict[str, Any] = Field(description="Agent configuration data")


class AgentConfigurationRead(BaseModel):
    id: UUID = Field(description="Agent ID")
    agent_type: AgentType = Field(description="Agent type")
    created_at: datetime = Field(description="Agent creation time")
    updated_at: datetime = Field(description="Agent update time")
    data: Dict[str, Any] = Field(description="Agent configuration data")
