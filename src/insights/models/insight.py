from datetime import datetime, timezone
from typing import Any
from uuid import uuid4, UUID

from sqlalchemy import Column, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlmodel import SQLModel, Field


class Insight(SQLModel, table=True):

    __tablename__ = "insight"
    __table_args__ = (
        Index("ix_created_at", "created_at"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(PG_UUID(as_uuid=True), primary_key=True),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        sa_column=Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    )
    data: dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=True)
    )