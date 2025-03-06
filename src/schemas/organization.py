"""Organization schemas for Performance Management System."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from uuid import UUID


class UnitType(str, Enum):
    """Enum for unit types based on frontend."""
    
    IT = "IT"
    MARKETING = "Marketing"
    SALES = "Sales"
    OPERATIONS = "Operations"
    CUSTOMER_SERVICE = "Customer Service"
    FINANCE = "Finance"


# Base schema for Department
class DepartmentBase(BaseModel):
    """Base schema for Department."""
    
    name: str
    code: str
    description: Optional[str] = None
    unit_type: Optional[UnitType] = None
    is_active: bool = True


# Schema for creating a new department
class DepartmentCreate(DepartmentBase):
    """Schema for creating a new Department."""
    
    parent_id: Optional[UUID] = None


# Schema for updating a department
class DepartmentUpdate(BaseModel):
    """Schema for updating a Department."""
    
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    unit_type: Optional[UnitType] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None


# Schema for department response
class DepartmentResponse(DepartmentBase):
    """Schema for Department in API responses."""
    
    id: UUID
    parent_id: Optional[UUID] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for department with children
class DepartmentWithChildrenResponse(DepartmentResponse):
    """Schema for Department with children in API responses."""
    
    children: List['DepartmentWithChildrenResponse'] = []
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Base schema for Position
class PositionBase(BaseModel):
    """Base schema for Position."""
    
    name: str
    code: str
    description: Optional[str] = None
    level: int = 0
    is_active: bool = True


# Schema for creating a new position
class PositionCreate(PositionBase):
    """Schema for creating a new Position."""
    
    department_id: UUID


# Schema for updating a position
class PositionUpdate(BaseModel):
    """Schema for updating a Position."""
    
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    department_id: Optional[UUID] = None
    is_active: Optional[bool] = None


# Schema for position response
class PositionResponse(PositionBase):
    """Schema for Position in API responses."""
    
    id: UUID
    department_id: UUID
    department_name: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for department query parameters
class DepartmentQueryParams(BaseModel):
    """Schema for Department query parameters."""
    
    name: Optional[str] = None
    code: Optional[str] = None
    unit_type: Optional[UnitType] = None
    is_active: Optional[bool] = None
    parent_id: Optional[UUID] = None
    include_children: bool = False
    page: int = 1
    page_size: int = 10


# Schema for position query parameters
class PositionQueryParams(BaseModel):
    """Schema for Position query parameters."""
    
    name: Optional[str] = None
    code: Optional[str] = None
    department_id: Optional[UUID] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None
    page: int = 1
    page_size: int = 10


# Avoid circular import issues with ForwardRef
DepartmentWithChildrenResponse.update_forward_refs()