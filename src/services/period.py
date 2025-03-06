"""Period service implementation for Performance Management System."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException, Depends, status
from sqlmodel import Session

from src.core.database import get_db
from src.models.period import Period, PeriodStatus
from src.repositories.period import PeriodRepository
from src.schemas.period import PeriodCreate, PeriodUpdate, PeriodStatusUpdate
from src.services.base import BaseService


class PeriodService(BaseService[Period, PeriodRepository]):
    """Service for Period management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=PeriodRepository, session=session)
    
    async def create_period(self, period_in: PeriodCreate, created_by: Optional[UUID] = None) -> Period:
        """Create a new period.
        
        Args:
            period_in: Period creation data
            created_by: UUID of the user creating the period
            
        Returns:
            Created Period object
            
        Raises:
            HTTPException: If a period with the same year, period and type already exists
        """
        # Check if period already exists
        existing_period = await self.repository.get_by_year_and_period(
            year=period_in.year,
            period=period_in.period,
            type=period_in.type
        )
        
        if existing_period:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A {period_in.type} period for year {period_in.year}, period {period_in.period} already exists"
            )
        
        # Create the new period
        # Convert to dict and add default values
        period_data = period_in.dict()
        period_data["status"] = PeriodStatus.DRAFT
        
        # Create name field for display purposes (e.g., "Jan-25" for monthly period 1 in 2025)
        name = self._generate_period_name(period_in.type, period_in.period, period_in.year)
        period_data["name"] = name
        
        return await self.repository.create(obj_in=period_data, created_by=created_by)
    
    async def update_period_status(
        self, 
        id: UUID, 
        status_update: PeriodStatusUpdate, 
        updated_by: Optional[UUID] = None
    ) -> Period:
        """Update the status of a period.
        
        Args:
            id: UUID of the period to update
            status_update: New status
            updated_by: UUID of the user updating the status
            
        Returns:
            Updated Period object
        """
        return await self.repository.update_status(id=id, status=status_update.status, updated_by=updated_by)
    
    async def get_active_period(self) -> Optional[Period]:
        """Get the currently active period.
        
        Returns:
            Active Period object if found, None otherwise
        """
        return await self.repository.get_active_period()
    
    async def search_periods(
        self,
        *,
        type: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Search periods with pagination.
        
        Args:
            type: Optional period type filter
            year: Optional year filter
            status: Optional status filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with results and pagination info
        """
        skip = (page - 1) * page_size
        
        # Get data with pagination
        periods = await self.repository.search(
            type=type,
            year=year,
            status=status,
            skip=skip,
            limit=page_size
        )
        
        # Get total count for pagination
        total = await self.repository.search_count(type=type, year=year, status=status)
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "data": periods,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    def _generate_period_name(self, period_type: str, period: str, year: int) -> str:
        """Generate a display name for the period.
        
        Args:
            period_type: Type of period (Monthly, Quarterly, Yearly)
            period: Period identifier (e.g., "1", "Q1", "FY")
            year: Year of the period
            
        Returns:
            Display name for the period (e.g., "Jan-25", "Q1-2025", "FY-2025")
        """
        year_str = str(year)[-2:]  # Get last 2 digits of year
        
        if period_type == "Monthly":
            # Map month number to abbreviation
            month_map = {
                "1": "Jan", "2": "Feb", "3": "Mar", "4": "Apr",
                "5": "May", "6": "Jun", "7": "Jul", "8": "Aug",
                "9": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
            }
            return f"{month_map.get(period, period)}-{year_str}"
        
        elif period_type == "Quarterly":
            return f"{period}-{year}"
        
        elif period_type == "Yearly":
            return f"FY-{year}"
        
        return f"{period}-{year}"  # Default fallback