"""Organization models for Performance Management System."""

from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from src.models.base import BaseModel, AuditMixin
from uuid import UUID

if TYPE_CHECKING:
    from src.models.user import User


class UnitType(str, Enum):
    """Enum for unit types based on frontend."""
    
    IT = "IT"
    MARKETING = "Marketing"
    SALES = "Sales"
    OPERATIONS = "Operations"
    CUSTOMER_SERVICE = "Customer Service"
    FINANCE = "Finance"


class Department(BaseModel, AuditMixin, table=True):
    """Department model for Performance Management System."""
    
    __tablename__ = "department"
    
    name: str = Field(index=True, nullable=False)
    code: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)
    unit_type: Optional[UnitType] = Field(default=None, nullable=True)
    
    # Organization hierarchy
    parent_id: Optional[UUID] = Field(default=None, foreign_key="department.id", nullable=True)
    
    # Relationships
    parent: Optional["Department"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": "Department.id"})
    children: List["Department"] = Relationship(back_populates="parent")
    positions: List["Position"] = Relationship(back_populates="department")
    users: List["User"] = Relationship(back_populates="department")


class Position(BaseModel, AuditMixin, table=True):
    """Position model for Performance Management System."""
    
    __tablename__ = "position"
    
    name: str = Field(index=True, nullable=False)
    code: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    level: int = Field(default=0, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    
    # Foreign keys
    department_id: UUID = Field(foreign_key="department.id", nullable=False)
    
    # Relationships
    department: Department = Relationship(back_populates="positions")
    users: List["User"] = Relationship(back_populates="position")