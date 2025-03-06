"""BSC (Balanced Scorecard) models for Performance Management System."""

from decimal import Decimal
from enum import Enum
from typing import Optional, List, TYPE_CHECKING, Union
from sqlmodel import Field, Relationship, SQLModel
from src.models.base import BaseModel, AuditMixin
from uuid import UUID

if TYPE_CHECKING:
    from src.models.period import Period
    from src.models.user import User


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


class BSCIndicator(BaseModel, AuditMixin, table=True):
    """BSC Indicator model for Performance Management System."""
    
    __tablename__ = "bsc_indicator"
    
    # Basic KPI information
    code: str = Field(index=True, nullable=False)
    kpi: str = Field(index=True, nullable=False)
    kpi_definition: str = Field(nullable=False)
    perspective: BSCPerspective = Field(nullable=False)
    
    # Measurement settings
    weight: Decimal = Field(default=Decimal("0.0"), nullable=False)
    uom: BSCUOM = Field(nullable=False)
    category: BSCCategory = Field(nullable=False)
    calculation: BSCCalculation = Field(nullable=False)
    target: str = Field(nullable=False)  # Stored as string to handle various types
    
    # Status
    is_active: bool = Field(default=True, nullable=False)
    
    # Additional info
    related_pic: Optional[str] = Field(default=None, nullable=True)
    
    # Foreign keys
    period_id: UUID = Field(foreign_key="period.id", nullable=False)
    
    # Relationships
    period: "Period" = Relationship(back_populates="bsc_indicators")
    actuals: List["BSCActual"] = Relationship(back_populates="indicator")


class BSCActual(BaseModel, AuditMixin, table=True):
    """BSC Actual model for tracking performance against indicators."""
    
    __tablename__ = "bsc_actual"
    
    # Actual values
    actual_value: str = Field(nullable=False)  # Stored as string to handle various types
    achievement: Decimal = Field(nullable=False)
    
    # Calculated scores
    score: Decimal = Field(nullable=False)
    active_weight: Decimal = Field(nullable=False)
    total_score: Decimal = Field(nullable=False)
    score_akhir: Decimal = Field(nullable=False)
    
    # Additional info
    problem_identification: Optional[str] = Field(default=None, nullable=True)
    corrective_action: Optional[str] = Field(default=None, nullable=True)
    
    # Foreign keys
    indicator_id: UUID = Field(foreign_key="bsc_indicator.id", nullable=False)
    
    # Relationships
    indicator: BSCIndicator = Relationship(back_populates="actuals")