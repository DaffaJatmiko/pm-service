"""Action Plan models for Performance Management System."""

from decimal import Decimal
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from src.models.base import BaseModel, AuditMixin
from uuid import UUID
from datetime import date

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.mpm import MPMTarget, MPMActual


class ActionPlanStatus(str, Enum):
    """Enum for action plan status based on frontend."""
    
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    OFF_TRACK = "Off Track"


class ActionPlan(BaseModel, AuditMixin, table=True):
    """Action Plan model for performance improvement initiatives."""
    
    __tablename__ = "action_plan"
    
    # Basic information
    title: str = Field(index=True, nullable=False)
    description: str = Field(nullable=False)
    due_date: date = Field(nullable=False)
    status: ActionPlanStatus = Field(default=ActionPlanStatus.PLANNED, nullable=False)
    progress: Decimal = Field(default=Decimal("0.0"), nullable=False)
    notes: Optional[str] = Field(default=None, nullable=True)
    
    # Foreign keys
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    approver_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    mpm_target_id: Optional[UUID] = Field(default=None, foreign_key="mpm_target.id", nullable=True)
    mpm_actual_id: Optional[UUID] = Field(default=None, foreign_key="mpm_actual.id", nullable=True)
    
    # Relationships
    user: "User" = Relationship(back_populates="action_plans", sa_relationship_kwargs={"foreign_keys": "ActionPlan.user_id"})
    approver: Optional["User"] = Relationship(back_populates="approved_action_plans", sa_relationship_kwargs={"foreign_keys": "ActionPlan.approver_id"})
    mpm_target: Optional["MPMTarget"] = Relationship(back_populates="action_plans", sa_relationship_kwargs={"foreign_keys": "ActionPlan.mpm_target_id"})
    mpm_actual: Optional["MPMActual"] = Relationship(sa_relationship_kwargs={"foreign_keys": "ActionPlan.mpm_actual_id"})