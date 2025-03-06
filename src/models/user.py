"""User model for Performance Management System."""

from datetime import date
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from src.models.base import BaseModel, AuditMixin
from uuid import UUID

if TYPE_CHECKING:
    from src.models.organization import Department, Position
    from src.models.bsc import BSCTarget, BSCActual
    from src.models.mpm import MPMTarget, MPMActual
    from src.models.ipm import IPMTarget, IPMActual
    from src.models.action_plan import ActionPlan


class UserRole(str, Enum):
    """Enum for user roles."""
    
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    HR = "hr"
    APPROVER = "approver"
    SENIOR_MANAGER = "senior_manager"


class User(BaseModel, AuditMixin, table=True):
    """User model for Performance Management System."""
    
    __tablename__ = "user"
    
    # Identity information
    employee_number: str = Field(unique=True, index=True, nullable=False)
    name: str = Field(nullable=False, index=True)
    email: str = Field(unique=True, index=True, nullable=False)
    phone: Optional[str] = Field(default=None, nullable=True)
    external_id: Optional[str] = Field(default=None, unique=True, index=True, nullable=True)  # ID from SSO system
    
    # Additional information
    join_date: Optional[date] = Field(default=None, nullable=True)
    birth_date: Optional[date] = Field(default=None, nullable=True)
    image_url: Optional[str] = Field(default=None, nullable=True)
    location: Optional[str] = Field(default=None, nullable=True)
    
    # Status and roles
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    roles: List[UserRole] = Field(default=[], sa_type="ARRAY(VARCHAR)")
    
    # Organizational relationships
    department_id: Optional[UUID] = Field(default=None, foreign_key="department.id", nullable=True)
    position_id: Optional[UUID] = Field(default=None, foreign_key="position.id", nullable=True)
    manager_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    
    # Relationships - will be populated by SQLModel relationship manager
    department: Optional["Department"] = Relationship(back_populates="users")
    position: Optional["Position"] = Relationship(back_populates="users")
    manager: Optional["User"] = Relationship(back_populates="subordinates", sa_relationship_kwargs={"remote_side": "User.id"})
    subordinates: List["User"] = Relationship(back_populates="manager")
    
    # Performance management relationships
    bsc_targets: List["BSCTarget"] = Relationship(back_populates="user", sa_relationship_kwargs={"primaryjoin": "User.id==BSCTarget.user_id"})
    bsc_actuals: List["BSCActual"] = Relationship(back_populates="user", sa_relationship_kwargs={"primaryjoin": "User.id==BSCActual.user_id"}) 
    
    mpm_targets: List["MPMTarget"] = Relationship(back_populates="user", sa_relationship_kwargs={"primaryjoin": "User.id==MPMTarget.user_id"})
    mpm_actuals: List["MPMActual"] = Relationship(back_populates="user", sa_relationship_kwargs={"primaryjoin": "User.id==MPMActual.user_id"})
    
    ipm_targets: List["IPMTarget"] = Relationship(back_populates="user", sa_relationship_kwargs={"primaryjoin": "User.id==IPMTarget.user_id"})
    ipm_actuals: List["IPMActual"] = Relationship(back_populates="user", sa_relationship_kwargs={"primaryjoin": "User.id==IPMActual.user_id"})
    
    action_plans: List["ActionPlan"] = Relationship(back_populates="user")
    approved_action_plans: List["ActionPlan"] = Relationship(back_populates="approver", sa_relationship_kwargs={"foreign_keys": "ActionPlan.approver_id"})