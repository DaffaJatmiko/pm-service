"""Base models and mixins for Performance Management System."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4


class BaseModel(SQLModel):
    """Base model with UUID primary key."""
    
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )


class AuditMixin(SQLModel):
    """Mixin to add audit fields to models."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)
    created_by: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    updated_by: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    is_deleted: bool = Field(default=False, nullable=False)