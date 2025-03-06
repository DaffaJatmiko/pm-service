"""BSC (Balanced Scorecard) schemas for Performance Management System."""

from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import date


class BSCPerspective(str, Enum):
    """Enum for BSC perspectives."""
    
    FINANCIAL = "Financial"
    CUSTOMER = "Customer"
    INTERNAL_BUSINESS_PROCESS = "Internal Business Process"
    LEARNING_GROWTH = "Learning & Growth"


class BSCUOM(str, Enum):
    """Enum for BSC Units of Measurement."""
    
    CURRENCY = "Currency"
    NUMBER = "Number"
    DAYS = "Days"
    PERCENTAGE = "%"
    KRITERIA = "Kriteria"


class BSCCategory(str, Enum):
    """Enum for BSC Categories."""
    
    MAX = "Max"
    MIN = "Min"
    ON_TARGET = "On Target"
    MAX_IS_100 = "Max is 100"
    MIN_IS_0 = "Min is 0"


class BSCCalculation(str, Enum):
    """Enum for BSC YTD calculation methods."""
    
    AVERAGE = "Average"
    ACCUMULATIVE = "Accumulative"
    LAST_VALUE = "Last Value"


class BSCType(str, Enum):
    """Enum for BSC types."""
    
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


# Base schema for BSC Indicator
class BSCIndicatorBase(BaseModel):
    """Base schema for BSC Indicator."""
    
    perspective: BSCPerspective
    code: str
    kpi: str
    kpi_definition: str
    weight: Decimal = Field(ge=0, le=100)
    uom: BSCUOM
    category: BSCCategory
    calculation: BSCCalculation


# Schema for creating a new BSC Indicator
class BSCIndicatorCreate(BSCIndicatorBase):
    """Schema for creating a new BSC Indicator."""
    
    period_id: UUID
    target: Union[Decimal, str]
    related_pic: Optional[str] = None


# Schema for updating BSC Indicator
class BSCIndicatorUpdate(BaseModel):
    """Schema for updating a BSC Indicator."""
    
    perspective: Optional[BSCPerspective] = None
    code: Optional[str] = None
    kpi: Optional[str] = None
    kpi_definition: Optional[str] = None
    weight: Optional[Decimal] = Field(default=None, ge=0, le=100)
    uom: Optional[BSCUOM] = None
    category: Optional[BSCCategory] = None
    calculation: Optional[BSCCalculation] = None
    period_id: Optional[UUID] = None
    target: Optional[Union[Decimal, str]] = None
    related_pic: Optional[str] = None
    is_active: Optional[bool] = None


# Schema for BSC Indicator response
class BSCIndicatorResponse(BSCIndicatorBase):
    """Schema for BSC Indicator in API responses."""
    
    id: UUID
    period_id: UUID
    target: Union[Decimal, str]
    related_pic: Optional[str] = None
    is_active: bool = True
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for BSC Actual
class BSCActualBase(BaseModel):
    """Base schema for BSC Actual."""
    
    actual_value: Union[Decimal, str]
    achievement: Decimal
    problem_identification: Optional[str] = None
    corrective_action: Optional[str] = None


# Schema for creating BSC Actual
class BSCActualCreate(BSCActualBase):
    """Schema for creating a BSC Actual."""
    
    indicator_id: UUID


# Schema for updating BSC Actual
class BSCActualUpdate(BaseModel):
    """Schema for updating a BSC Actual."""
    
    actual_value: Optional[Union[Decimal, str]] = None
    achievement: Optional[Decimal] = None
    problem_identification: Optional[str] = None
    corrective_action: Optional[str] = None


# Schema for BSC Actual response
class BSCActualResponse(BSCActualBase):
    """Schema for BSC Actual in API responses."""
    
    id: UUID
    indicator_id: UUID
    score: Decimal
    active_weight: Decimal
    total_score: Decimal
    score_akhir: Decimal
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for BSC Dashboard item
class BSCDashboardItem(BaseModel):
    """Schema for BSC Dashboard item in responses."""
    
    indicator: BSCIndicatorResponse
    actual: Optional[BSCActualResponse] = None


# Schema for BSC Dashboard by Perspective
class BSCDashboardPerspective(BaseModel):
    """Schema for BSC Dashboard grouped by perspective."""
    
    perspective: BSCPerspective
    items: List[BSCDashboardItem]
    total_weight: Decimal
    total_score: Decimal
    total_active_weight: Decimal
    total_score_akhir: Decimal


# Schema for complete BSC Dashboard
class BSCDashboardResponse(BaseModel):
    """Schema for complete BSC Dashboard."""
    
    period_id: UUID
    period_name: str
    bsc_type: BSCType
    perspectives: List[BSCDashboardPerspective]
    total_weight: Decimal
    total_score: Decimal
    total_active_weight: Decimal
    total_score_akhir: Decimal


# Schema for BSC query parameters
class BSCQueryParams(BaseModel):
    """Schema for BSC query parameters."""
    
    perspective: Optional[BSCPerspective] = None
    period_id: Optional[UUID] = None
    bsc_type: Optional[BSCType] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None
    page: int = 1
    page_size: int = 10


# Schema for bulk import BSC indicators
class BSCBulkImportItem(BSCIndicatorCreate):
    """Schema for bulk import BSC indicator item."""
    
    pass


class BSCBulkImport(BaseModel):
    """Schema for bulk import BSC indicators."""
    
    indicators: List[BSCBulkImportItem]