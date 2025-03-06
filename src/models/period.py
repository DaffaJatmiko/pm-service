"""Period models for Performance Management System."""

from datetime import date
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from src.models.base import BaseModel, AuditMixin
from uuid import UUID

if TYPE_CHECKING:
    from src.models.bsc import BSCPeriod, BSCIndicator
    from src.models.mpm import MPMPeriod, MPMIndicator
    from src.models.ipm import IPMPeriod



class PeriodType(str, Enum):
    """Enum for period types based on frontend."""
    
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    YEARLY = "Yearly"


class PeriodStatus(str, Enum):
    """Enum for period status based on frontend."""
    
    DRAFT = "Draft"
    ACTIVE = "Active"
    CLOSED = "Closed"


class Period(BaseModel, AuditMixin, table=True):
    """Period model for Performance Management System."""
    
    __tablename__ = "period"
    
    # Basic period information
    type: PeriodType = Field(nullable=False)
    year: int = Field(nullable=False)
    period: str = Field(nullable=False)  # For months: "1", "2", etc. For quarters: "Q1", "Q2", etc.
    name: str = Field(index=True, nullable=False)  # Display name like "Jan-25", "Q1-2025"
    
    # Timeframe
    start_date: date = Field(nullable=False)
    end_date: date = Field(nullable=False)
    
    # Status
    status: PeriodStatus = Field(default=PeriodStatus.DRAFT, nullable=False)
    
    # Relationships to performance periods
    bsc_periods: List["BSCPeriod"] = Relationship(back_populates="period")
    mpm_periods: List["MPMPeriod"] = Relationship(back_populates="period")
    ipm_periods: List["IPMPeriod"] = Relationship(back_populates="period")
    bsc_indicators: List["BSCIndicator"] = Relationship(back_populates="period")
    mpm_indicators: List["MPMIndicator"] = Relationship(back_populates="period")
    
    class Config:
        """SQLModel configuration."""
        
        # Unique constraint for year and period combination
        table_name = "period"
        schema_extra = {
            "unique_together": [("year", "period", "type")]
        }