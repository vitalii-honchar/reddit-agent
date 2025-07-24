from pydantic import BaseModel, Field
from uuid import UUID

class Agent(BaseModel):
    id: UUID = Field(description="Agent ID")
    name: str = Field(description="Agent name")
    description: str = Field(description="Agent description")