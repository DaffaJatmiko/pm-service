"""Period schemas for Performance Management System."""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from uuid import UUID


class PeriodType(str, Enum):
    """Enum for period types."""
    
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


class PeriodStatus(str, Enum):
    """Enum for period status."""
    
    DRAFT = "Draft"
    ACTIVE = "Active"
    CLOSED = "Closed"


# Base schema with common attributes
class PeriodBase(BaseModel):
    """Base schema for Period."""
    
    type: PeriodType
    year: int
    period: str
    start_date: date
    end_date: date

    @validator('year')
    def validate_year(cls, v):
        """Validate that year is reasonable."""
        current_year = datetime.now().year
        if v < 2000 or v > current_year + 10:
            raise ValueError(f"Year must be between 2000 and {current_year + 10}")
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end_date is after start_date."""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("End date must be after start date")
        return v


# Schema for creating a new period
class PeriodCreate(PeriodBase):
    """Schema for creating a new Period."""
    
    pass


# Schema for updating an existing period
class PeriodUpdate(BaseModel):
    """Schema for updating a Period."""
    
    type: Optional[PeriodType] = None
    year: Optional[int] = None
    period: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[PeriodStatus] = None

    @validator('year')
    def validate_year(cls, v):
        """Validate that year is reasonable if provided."""
        if v is not None:
            current_year = datetime.now().year
            if v < 2000 or v > current_year + 10:
                raise ValueError(f"Year must be between 2000 and {current_year + 10}")
        return v


# Schema for representing a period in responses
class PeriodResponse(PeriodBase):
    """Schema for Period in API responses."""
    
    id: UUID
    status: PeriodStatus
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for period list query parameters
class PeriodQueryParams(BaseModel):
    """Schema for Period query parameters."""
    
    type: Optional[PeriodType] = None
    year: Optional[int] = None
    status: Optional[PeriodStatus] = None
    page: int = 1
    page_size: int = 10


# Schema for changing period status
class PeriodStatusUpdate(BaseModel):
    """Schema for updating Period status."""
    
    status: PeriodStatus