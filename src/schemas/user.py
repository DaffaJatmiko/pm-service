"""User schemas for Performance Management System."""

from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID


class UserRole(str, Enum):
    """Enum for user roles."""
    
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    HR = "hr"
    APPROVER = "approver"
    SENIOR_MANAGER = "senior_manager"


class UserStatus(str, Enum):
    """Enum for user status."""
    
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


# Base schema with common attributes
class UserBase(BaseModel):
    """Base schema for User."""
    
    name: str
    email: EmailStr
    employee_number: str
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    

# Schema for creating a new user
class UserCreate(UserBase):
    """Schema for creating a new User."""
    
    roles: List[UserRole] = [UserRole.EMPLOYEE]
    join_date: Optional[date] = None
    birth_date: Optional[date] = None
    status: UserStatus = UserStatus.ACTIVE
    external_id: Optional[str] = None  # ID from SSO system


# Schema for updating an existing user
class UserUpdate(BaseModel):
    """Schema for updating a User."""
    
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    roles: Optional[List[UserRole]] = None
    status: Optional[UserStatus] = None
    join_date: Optional[date] = None
    birth_date: Optional[date] = None
    image_url: Optional[str] = None
    external_id: Optional[str] = None  # ID from SSO system


# Schema for representing a user in responses (without sensitive info)
class UserResponse(BaseModel):
    """Schema for User in API responses."""
    
    id: UUID
    name: str
    email: EmailStr
    employee_number: str
    phone: Optional[str] = None
    department_id: Optional[UUID] = None
    department: Optional[str] = None
    position_id: Optional[UUID] = None
    position: Optional[str] = None
    manager_id: Optional[UUID] = None
    report_to: Optional[str] = None
    location: Optional[str] = None
    join_date: Optional[date] = None
    roles: List[UserRole] = []
    status: UserStatus
    image_url: Optional[str] = None
    external_id: Optional[str] = None  # ID from SSO system
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for detailed user info (including performance data)
class PerformanceData(BaseModel):
    """Schema for user performance data."""
    
    mpm_completion_rate: Optional[float] = None
    ipm_completion_rate: Optional[float] = None
    overall_score: Optional[float] = None
    performance_trend: Optional[List[float]] = None


class UserDetailResponse(UserResponse):
    """Schema for detailed User in API responses."""
    
    performance_data: Optional[PerformanceData] = None


# Schema for linking a user with SSO
class UserSSOLink(BaseModel):
    """Schema for linking a user with SSO system."""
    
    external_id: str  # ID from SSO system


# Schema for user list query parameters
class UserQueryParams(BaseModel):
    """Schema for User query parameters."""
    
    name: Optional[str] = None
    email: Optional[str] = None
    employee_number: Optional[str] = None
    department_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    external_id: Optional[str] = None
    page: int = 1
    page_size: int = 10