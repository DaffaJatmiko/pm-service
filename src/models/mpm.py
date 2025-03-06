"""MPM (Management Performance Measurement) models for Performance Management System."""

from decimal import Decimal
from enum import Enum
from typing import Optional, List, TYPE_CHECKING, Dict
from sqlmodel import Field, Relationship, SQLModel
from src.models.base import BaseModel, AuditMixin
from uuid import UUID
from datetime import date

if TYPE_CHECKING:
    from src.models.period import Period
    from src.models.user import User


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


class MPMIndicator(BaseModel, AuditMixin, table=True):
    """MPM Indicator model for Performance Management System."""
    
    __tablename__ = "mpm_indicator"
    
    # Basic KPI information
    kpi: str = Field(index=True, nullable=False)
    kpi_definition: str = Field(nullable=False)
    weight: Decimal = Field(default=Decimal("0.0"), nullable=False)
    uom: MPMUOM = Field(nullable=False)
    category: MPMCategory = Field(nullable=False)
    ytd_calculation: MPMCalculation = Field(nullable=False)
    kpi_number: Optional[int] = Field(default=None, nullable=True)
    perspective: Optional[MPMPerspective] = Field(default=None, nullable=True)
    
    # Target
    target: Decimal = Field(nullable=False)
    
    # Status
    is_active: bool = Field(default=True, nullable=False)
    
    # Foreign keys
    period_id: UUID = Field(foreign_key="period.id", nullable=False)
    
    # Relationships
    period: "Period" = Relationship(back_populates="mpm_indicators")
    monthly_targets: List["MPMMonthlyTarget"] = Relationship(back_populates="indicator")
    action_plans: List["MPMActionPlan"] = Relationship(back_populates="indicator")
    actuals: List["MPMActual"] = Relationship(back_populates="indicator")


class MPMMonthlyTarget(BaseModel, AuditMixin, table=True):
    """MPM Monthly Target model for Performance Management System."""
    
    __tablename__ = "mpm_monthly_target"
    
    # Target information
    month: str = Field(nullable=False)  # Format: "Jan-25", "Feb-25", etc.
    target_value: Decimal = Field(nullable=False)
    
    # Foreign keys
    indicator_id: UUID = Field(foreign_key="mpm_indicator.id", nullable=False)
    
    # Relationships
    indicator: MPMIndicator = Relationship(back_populates="monthly_targets")


class MPMActionPlan(BaseModel, AuditMixin, table=True):
    """MPM Action Plan model for Performance Management System."""
    
    __tablename__ = "mpm_action_plan"
    
    # Action Plan information
    description: str = Field(nullable=False)
    responsible_person: str = Field(nullable=False)
    deadline: date = Field(nullable=False)
    status: MPMStatus = Field(default=MPMStatus.ON_TRACK, nullable=False)
    
    # Foreign keys
    indicator_id: UUID = Field(foreign_key="mpm_indicator.id", nullable=False)
    
    # Relationships
    indicator: MPMIndicator = Relationship(back_populates="action_plans")
    quarterly_data: List["MPMQuarterlyData"] = Relationship(back_populates="action_plan")


class MPMQuarterlyData(BaseModel, AuditMixin, table=True):
    """MPM Quarterly Data model for Performance Management System."""
    
    __tablename__ = "mpm_quarterly_data"
    
    # Quarterly data
    quarter: str = Field(nullable=False)  # Format: "Q1", "Q2", "Q3", "Q4"
    target_value: Decimal = Field(nullable=False)
    actual_value: Optional[Decimal] = Field(default=None, nullable=True)
    
    # Foreign keys
    action_plan_id: UUID = Field(foreign_key="mpm_action_plan.id", nullable=False)
    
    # Relationships
    action_plan: MPMActionPlan = Relationship(back_populates="quarterly_data")


class MPMActual(BaseModel, AuditMixin, table=True):
    """MPM Actual model for tracking performance against indicators."""
    
    __tablename__ = "mpm_actual"
    
    # Actual values
    actual_value: Decimal = Field(nullable=False)
    achievement: Decimal = Field(nullable=False)
    
    # Calculated score
    score: Decimal = Field(nullable=False)
    
    # Additional info
    problem_identification: Optional[str] = Field(default=None, nullable=True)
    corrective_action: Optional[str] = Field(default=None, nullable=True)
    
    # Foreign keys
    indicator_id: UUID = Field(foreign_key="mpm_indicator.id", nullable=False)
    
    # Relationships
    indicator: MPMIndicator = Relationship(back_populates="actuals")


class MPMApprover(BaseModel, AuditMixin, table=True):
    """MPM Approver model for Performance Management System."""
    
    __tablename__ = "mpm_approver"
    
    # Approver information
    name: str = Field(nullable=False)
    position: str = Field(nullable=False)
    department: str = Field(nullable=False)
    
    # Foreign keys
    user_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    
    # Relationships
    user: Optional["User"] = Relationship()