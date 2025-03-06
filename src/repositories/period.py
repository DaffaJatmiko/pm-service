"""Period repository implementation for Performance Management System."""

from typing import Dict, List, Optional, Any
from sqlmodel import Session, select, col, or_
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime

from src.models.period import Period, PeriodStatus
from src.repositories.base import BaseRepository


class PeriodRepository(BaseRepository[Period]):
    """Repository for Period model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=Period, session=session)
    
    async def get_by_year_and_period(self, year: int, period: str, type: str) -> Optional[Period]:
        """Get a period by year and period identifier.
        
        Args:
            year: Year of the period
            period: Period identifier (e.g., "1", "Q1", "FY")
            type: Type of period (Monthly, Quarterly, Yearly)
            
        Returns:
            Period object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.year) == year,
            col(self.model.period) == period,
            col(self.model.type) == type,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def get_active_period(self) -> Optional[Period]:
        """Get the currently active period.
        
        Returns:
            Active Period object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.status) == PeriodStatus.ACTIVE,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def update_status(self, id: UUID, status: PeriodStatus, updated_by: Optional[UUID] = None) -> Period:
        """Update the status of a period.
        
        Args:
            id: UUID of the period to update
            status: New status
            updated_by: UUID of the user updating the status
            
        Returns:
            Updated Period object
            
        Raises:
            HTTPException: If period not found or if trying to activate when another is already active
        """
        db_obj = await self.get_or_404(id)
        
        # Check if trying to activate a period when another is already active
        if status == PeriodStatus.ACTIVE:
            active_period = await self.get_active_period()
            if active_period and active_period.id != id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Another period is already active. Please close it first."
                )
        
        # Update the status
        db_obj.status = status
        
        # Update audit fields
        if updated_by:
            db_obj.updated_by = updated_by
        db_obj.updated_at = datetime.utcnow()
        
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj
    
    async def search(
        self,
        *,
        type: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Period]:
        """Search periods with various filters.
        
        Args:
            type: Optional period type filter
            year: Optional year filter
            status: Optional status filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Period objects matching the criteria
        """
        filters = {}
        if type is not None:
            filters["type"] = type
        if year is not None:
            filters["year"] = year
        if status is not None:
            filters["status"] = status
        
        return await self.get_multi(skip=skip, limit=limit, filters=filters)
    
    async def search_count(
        self,
        *,
        type: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[str] = None
    ) -> int:
        """Count periods matching search criteria.
        
        Args:
            type: Optional period type filter
            year: Optional year filter
            status: Optional status filter
            
        Returns:
            Number of matching periods
        """
        filters = {}
        if type is not None:
            filters["type"] = type
        if year is not None:
            filters["year"] = year
        if status is not None:
            filters["status"] = status
        
        return await self.count(filters=filters)