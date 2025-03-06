"""IPM (Individual Performance Management) models for Performance Management System."""

from decimal import Decimal
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from src.models.base import BaseModel, AuditMixin
from uuid import UUID
from datetime import date

if TYPE_CHECKING:
    from src.models.period import Period
    from src.models.user import User


class IPMStatus(str, Enum):
    """Enum for IPM status based on frontend."""
    
    PENDING = "Pending"
    EVIDENCE_SUBMITTED = "Evidence Submitted"
    APPROVED_BY_MANAGER = "Approved by Manager"
    VALIDATED_BY_SM = "Validated by SM"


class IPMEvidenceStatus(str, Enum):
    """Enum for IPM evidence status based on frontend."""
    
    NOT_SUBMITTED = "Not Submitted"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class IPMPerspective(str, Enum):
    """Enum for IPM perspectives based on frontend."""
    
    FINANCIAL = "Financial"
    CUSTOMER = "Customer"
    INTERNAL_PROCESS = "Internal Business Process"
    LEARNING_GROWTH = "Learning & Growth"


class IPMPeriod(BaseModel, AuditMixin, table=True):
    """IPM Period model for setting up IPM periods linked to main periods."""
    
    __tablename__ = "ipm_period"
    
    name: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)
    is_locked: bool = Field(default=False, nullable=False)
    
    # Foreign keys
    period_id: UUID = Field(foreign_key="period.id", nullable=False)
    
    # Relationships
    period: "Period" = Relationship(back_populates="ipm_periods")
    indicators: List["IPMIndicator"] = Relationship(back_populates="ipm_period")


class IPMIndicator(BaseModel, AuditMixin, table=True):
    """IPM Indicator model for defining KPIs in the Individual Performance Management."""
    
    __tablename__ = "ipm_indicator"
    
    # Basic KPI information
    title: str = Field(index=True, nullable=False)
    description: str = Field(nullable=False)
    perspective: IPMPerspective = Field(nullable=False)
    
    # Measurement settings
    weight: Decimal = Field(default=Decimal("0.0"), nullable=False)
    target_date: Optional[date] = Field(default=None, nullable=True)
    
    # Status
    is_active: bool = Field(default=True, nullable=False)
    
    # Foreign keys
    ipm_period_id: UUID = Field(foreign_key="ipm_period.id", nullable=False)
    
    # Relationships
    ipm_period: IPMPeriod = Relationship(back_populates="indicators")
    targets: List["IPMTarget"] = Relationship(back_populates="indicator")
    actuals: List["IPMActual"] = Relationship(back_populates="indicator")


class IPMEvidence(BaseModel, AuditMixin, table=True):
    """IPM Evidence model for tracking evidence submissions."""
    
    __tablename__ = "ipm_evidence"
    
    file_name: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    upload_date: date = Field(nullable=False)
    status: IPMEvidenceStatus = Field(default=IPMEvidenceStatus.SUBMITTED, nullable=False)
    comments: Optional[str] = Field(default=None, nullable=True)
    review_date: Optional[date] = Field(default=None, nullable=True)
    
    # Foreign keys
    actual_id: UUID = Field(foreign_key="ipm_actual.id", nullable=False)
    reviewed_by_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    
    # Relationships
    actual: "IPMActual" = Relationship(back_populates="evidence")
    reviewed_by: Optional["User"] = Relationship()


class IPMTarget(BaseModel, AuditMixin, table=True):
    """IPM Target model for individual targets."""
    
    __tablename__ = "ipm_target"
    
    target_value: Optional[str] = Field(default=None, nullable=True)  # Can be textual for some IPM targets
    target_numeric: Optional[Decimal] = Field(default=None, nullable=True)  # For numeric targets
    notes: Optional[str] = Field(default=None, nullable=True)
    status: str = Field(default="draft", nullable=False)
    
    # Foreign keys
    indicator_id: UUID = Field(foreign_key="ipm_indicator.id", nullable=False)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    approver_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    
    # Relationships
    indicator: IPMIndicator = Relationship(back_populates="targets")
    user: "User" = Relationship(back_populates="ipm_targets", sa_relationship_kwargs={"foreign_keys": "IPMTarget.user_id"})
    approver: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "IPMTarget.approver_id"})
    actuals: List["IPMActual"] = Relationship(back_populates="target")


class IPMActual(BaseModel, AuditMixin, table=True):
    """IPM Actual model for tracking actual performance against targets."""
    
    __tablename__ = "ipm_actual"
    
    actual_value: Optional[str] = Field(default=None, nullable=True)  # Can be textual
    actual_numeric: Optional[Decimal] = Field(default=None, nullable=True)  # For numeric actuals
    achievement: Optional[Decimal] = Field(default=None, nullable=True)
    score: Optional[Decimal] = Field(default=None, nullable=True)
    status: IPMStatus = Field(default=IPMStatus.PENDING, nullable=False)
    
    # Foreign keys
    indicator_id: UUID = Field(foreign_key="ipm_indicator.id", nullable=False)
    target_id: UUID = Field(foreign_key="ipm_target.id", nullable=False)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    approver_id: Optional[UUID] = Field(default=None, foreign_key="user.id", nullable=True)
    
    # Relationships
    indicator: IPMIndicator = Relationship(back_populates="actuals")
    target: IPMTarget = Relationship(back_populates="actuals")
    user: "User" = Relationship(back_populates="ipm_actuals", sa_relationship_kwargs={"foreign_keys": "IPMActual.user_id"})
    approver: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "IPMActual.approver_id"})
    evidence: List["IPMEvidence"] = Relationship(back_populates="actual")