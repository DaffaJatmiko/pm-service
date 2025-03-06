"""MPM (Management Performance Measurement) schemas for Performance Management System."""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID


class MPMPerspective(str, Enum):
    """Enum for MPM perspectives."""
    
    FINANCIAL = "Financial"
    CUSTOMER = "Customer"
    INTERNAL_BUSINESS_PROCESS = "Internal Business Process"
    LEARNING_GROWTH = "Learning & Growth"


class MPMUOM(str, Enum):
    """Enum for MPM Units of Measurement."""
    
    NUMBER = "Number"
    PERCENTAGE = "%"
    DAYS = "Days"
    KRITERIA = "Kriteria"
    NUMBER_TON = "Number (Ton)"


class MPMCategory(str, Enum):
    """Enum for MPM Categories."""
    
    MAX = "Max"
    MIN = "Min"
    ON_TARGET = "On Target"


class MPMCalculation(str, Enum):
    """Enum for MPM YTD calculation methods."""
    
    ACCUMULATIVE = "Accumulative"
    AVERAGE = "Average"
    LAST_VALUE = "Last Value"


class MPMStatus(str, Enum):
    """Enum for MPM action plan status."""
    
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    OFF_TRACK = "Off Track"


# Base schema for MPM Indicator
class MPMIndicatorBase(BaseModel):
    """Base schema for MPM Indicator."""
    
    kpi: str
    kpi_definition: str
    weight: Decimal = Field(ge=0, le=100)
    uom: MPMUOM
    category: MPMCategory
    ytd_calculation: MPMCalculation
    kpi_number: Optional[int] = None
    perspective: Optional[MPMPerspective] = None


# Schema for creating a new MPM Indicator
class MPMIndicatorCreate(MPMIndicatorBase):
    """Schema for creating a new MPM Indicator."""
    
    period_id: UUID
    target: Decimal


# Schema for updating MPM Indicator
class MPMIndicatorUpdate(BaseModel):
    """Schema for updating a MPM Indicator."""
    
    kpi: Optional[str] = None
    kpi_definition: Optional[str] = None
    weight: Optional[Decimal] = Field(default=None, ge=0, le=100)
    uom: Optional[MPMUOM] = None
    category: Optional[MPMCategory] = None
    ytd_calculation: Optional[MPMCalculation] = None
    kpi_number: Optional[int] = None
    perspective: Optional[MPMPerspective] = None
    target: Optional[Decimal] = None
    is_active: Optional[bool] = None


# Schema for MPM Indicator response
class MPMIndicatorResponse(MPMIndicatorBase):
    """Schema for MPM Indicator in API responses."""
    
    id: UUID
    period_id: UUID
    target: Decimal
    is_active: bool = True
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for Monthly Target in MPM
class MPMMonthlyTargetBase(BaseModel):
    """Base schema for MPM Monthly Target."""
    
    month: str  # Format: "Jan-25", "Feb-25", etc.
    target_value: Decimal


# Schema for creating MPM Monthly Target
class MPMMonthlyTargetCreate(MPMMonthlyTargetBase):
    """Schema for creating a MPM Monthly Target."""
    
    indicator_id: UUID


# Schema for updating MPM Monthly Target
class MPMMonthlyTargetUpdate(BaseModel):
    """Schema for updating a MPM Monthly Target."""
    
    target_value: Optional[Decimal] = None


# Schema for MPM Monthly Target response
class MPMMonthlyTargetResponse(MPMMonthlyTargetBase):
    """Schema for MPM Monthly Target in API responses."""
    
    id: UUID
    indicator_id: UUID
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for Action Plan
class MPMActionPlanBase(BaseModel):
    """Base schema for MPM Action Plan."""
    
    description: str
    responsible_person: str
    deadline: date


# Schema for creating Action Plan
class MPMActionPlanCreate(MPMActionPlanBase):
    """Schema for creating a MPM Action Plan."""
    
    indicator_id: UUID


# Schema for updating Action Plan
class MPMActionPlanUpdate(BaseModel):
    """Schema for updating a MPM Action Plan."""
    
    description: Optional[str] = None
    responsible_person: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[MPMStatus] = None


# Schema for Action Plan response
class MPMActionPlanResponse(MPMActionPlanBase):
    """Schema for MPM Action Plan in API responses."""
    
    id: UUID
    indicator_id: UUID
    status: MPMStatus
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for Quarterly data in Action Plan
class MPMQuarterlyDataBase(BaseModel):
    """Base schema for MPM Quarterly Data."""
    
    quarter: str  # Format: "Q1", "Q2", "Q3", "Q4"
    target_value: Decimal
    actual_value: Optional[Decimal] = None


# Schema for creating MPM Quarterly Data
class MPMQuarterlyDataCreate(MPMQuarterlyDataBase):
    """Schema for creating a MPM Quarterly Data."""
    
    action_plan_id: UUID


# Schema for updating MPM Quarterly Data
class MPMQuarterlyDataUpdate(BaseModel):
    """Schema for updating a MPM Quarterly Data."""
    
    target_value: Optional[Decimal] = None
    actual_value: Optional[Decimal] = None


# Schema for MPM Quarterly Data response
class MPMQuarterlyDataResponse(MPMQuarterlyDataBase):
    """Schema for MPM Quarterly Data in API responses."""
    
    id: UUID
    action_plan_id: UUID
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for MPM Actual
class MPMActualBase(BaseModel):
    """Base schema for MPM Actual."""
    
    actual_value: Decimal
    achievement: Decimal
    problem_identification: Optional[str] = None
    corrective_action: Optional[str] = None


# Schema for creating MPM Actual
class MPMActualCreate(MPMActualBase):
    """Schema for creating a MPM Actual."""
    
    indicator_id: UUID


# Schema for updating MPM Actual
class MPMActualUpdate(BaseModel):
    """Schema for updating a MPM Actual."""
    
    actual_value: Optional[Decimal] = None
    achievement: Optional[Decimal] = None
    problem_identification: Optional[str] = None
    corrective_action: Optional[str] = None


# Schema for MPM Actual response
class MPMActualResponse(MPMActualBase):
    """Schema for MPM Actual in API responses."""
    
    id: UUID
    indicator_id: UUID
    score: Decimal
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for Approver
class MPMApproverBase(BaseModel):
    """Base schema for MPM Approver."""
    
    name: str
    position: str
    department: str


# Schema for creating Approver
class MPMApproverCreate(MPMApproverBase):
    """Schema for creating a MPM Approver."""
    
    user_id: Optional[UUID] = None


# Schema for updating Approver
class MPMApproverUpdate(BaseModel):
    """Schema for updating a MPM Approver."""
    
    name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    user_id: Optional[UUID] = None


# Schema for Approver response
class MPMApproverResponse(MPMApproverBase):
    """Schema for MPM Approver in API responses."""
    
    id: UUID
    user_id: Optional[UUID] = None
    created_at: date
    updated_at: Optional[date] = None
    
    class Config:
        """Pydantic configuration."""
        
        orm_mode = True


# Schema for MPM Indicator with related data
class MPMIndicatorWithRelatedResponse(MPMIndicatorResponse):
    """Schema for MPM Indicator with related data in API responses."""
    
    monthly_targets: List[MPMMonthlyTargetResponse] = []
    action_plans: List[MPMActionPlanResponse] = []
    actuals: List[MPMActualResponse] = []


# Schema for MPM Action Plan with related data
class MPMActionPlanWithRelatedResponse(MPMActionPlanResponse):
    """Schema for MPM Action Plan with related data in API responses."""
    
    quarterly_data: List[MPMQuarterlyDataResponse] = []
    indicator: Optional[MPMIndicatorResponse] = None


# Schema for MPM dashboard item
class MPMDashboardItem(BaseModel):
    """Schema for MPM Dashboard item in responses."""
    
    indicator: MPMIndicatorResponse
    monthly_targets: Dict[str, Decimal] = {}
    actual: Optional[MPMActualResponse] = None
    action_plans: List[MPMActionPlanResponse] = []


# Schema for MPM dashboard by perspective
class MPMDashboardPerspective(BaseModel):
    """Schema for MPM Dashboard grouped by perspective."""
    
    perspective: MPMPerspective
    items: List[MPMDashboardItem] = []
    total_weight: Decimal = Decimal(0)
    total_score: Decimal = Decimal(0)


# Schema for complete MPM dashboard
class MPMDashboardResponse(BaseModel):
    """Schema for complete MPM Dashboard."""
    
    period_id: UUID
    period_name: str
    perspectives: List[MPMDashboardPerspective] = []
    total_weight: Decimal = Decimal(0)
    total_score: Decimal = Decimal(0)


# Schema for quarterly summary
class MPMQuarterlySummary(BaseModel):
    """Schema for MPM Quarterly Summary."""
    
    quarter: str  # Format: "Q1 2023", "Q2 2023", etc.
    completion: str  # Format: "85%"
    on_track_count: int
    at_risk_count: int
    off_track_count: int


# Schema for MPM query parameters
class MPMQueryParams(BaseModel):
    """Schema for MPM query parameters."""
    
    perspective: Optional[MPMPerspective] = None
    period_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    page: int = 1
    page_size: int = 10


# Schema for bulk import MPM indicators
class MPMBulkImportItem(MPMIndicatorCreate):
    """Schema for bulk import MPM indicator item."""
    
    monthly_targets: Dict[str, Decimal] = {}
    action_plans: List[MPMActionPlanBase] = []


class MPMBulkImport(BaseModel):
    """Schema for bulk import MPM indicators."""
    
    indicators: List[MPMBulkImportItem]