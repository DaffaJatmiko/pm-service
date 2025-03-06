"""BSC (Balanced Scorecard) service implementation for Performance Management System."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from fastapi import HTTPException, Depends, status
from sqlmodel import Session
from decimal import Decimal

from src.core.database import get_db
from src.models.bsc import BSCIndicator, BSCActual, BSCPerspective, BSCUOM, BSCCategory, BSCCalculation
from src.repositories.bsc import BSCIndicatorRepository, BSCActualRepository
from src.schemas.bsc import (
    BSCIndicatorCreate, 
    BSCIndicatorUpdate, 
    BSCActualCreate, 
    BSCActualUpdate,
    BSCBulkImport
)
from src.services.base import BaseService


class BSCIndicatorService(BaseService[BSCIndicator, BSCIndicatorRepository]):
    """Service for BSC Indicator management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=BSCIndicatorRepository, session=session)
    
    async def create_indicator(self, indicator_in: BSCIndicatorCreate, created_by: Optional[UUID] = None) -> BSCIndicator:
        """Create a new BSC indicator.
        
        Args:
            indicator_in: BSC indicator creation data
            created_by: UUID of the user creating the indicator
            
        Returns:
            Created BSCIndicator object
            
        Raises:
            HTTPException: If an indicator with the same code already exists for the period
        """
        # Check if indicator already exists for this period
        existing_indicator = await self.repository.get_by_code(
            code=indicator_in.code, 
            period_id=indicator_in.period_id
        )
        
        if existing_indicator:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A BSC indicator with code {indicator_in.code} already exists for this period"
            )
        
        # Create the new indicator
        return await self.repository.create(obj_in=indicator_in.dict(), created_by=created_by)
    
    async def update_indicator(
        self, 
        indicator_id: UUID, 
        indicator_in: BSCIndicatorUpdate, 
        updated_by: Optional[UUID] = None
    ) -> BSCIndicator:
        """Update a BSC indicator.
        
        Args:
            indicator_id: UUID of the indicator to update
            indicator_in: BSC indicator update data
            updated_by: UUID of the user updating the indicator
            
        Returns:
            Updated BSCIndicator object
            
        Raises:
            HTTPException: If the indicator is not found or if code is being updated to one that already exists
        """
        # Get existing indicator
        db_indicator = await self.repository.get_or_404(id=indicator_id)
        
        # Check if code is being updated and already exists
        if indicator_in.code and indicator_in.code != db_indicator.code:
            period_id = indicator_in.period_id or db_indicator.period_id
            existing_indicator = await self.repository.get_by_code(
                code=indicator_in.code, 
                period_id=period_id
            )
            
            if existing_indicator and existing_indicator.id != indicator_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A BSC indicator with code {indicator_in.code} already exists for this period"
                )
        
        # Update the indicator
        return await self.repository.update(
            db_obj=db_indicator, 
            obj_in=indicator_in.dict(exclude_unset=True), 
            updated_by=updated_by
        )
    
    async def get_indicator_with_actuals(self, indicator_id: UUID) -> Dict[str, Any]:
        """Get a BSC indicator with its actuals.
        
        Args:
            indicator_id: UUID of the indicator
            
        Returns:
            Dict with indicator and its actuals
        """
        return await self.repository.get_by_id_with_actuals(id=indicator_id)
    
    async def get_indicators_by_period(self, period_id: UUID) -> List[BSCIndicator]:
        """Get all BSC indicators for a period.
        
        Args:
            period_id: Period ID
            
        Returns:
            List of BSCIndicator objects
        """
        return await self.repository.get_by_period(period_id=period_id)
    
    async def get_indicators_by_perspective(self, perspective: BSCPerspective, period_id: UUID) -> List[BSCIndicator]:
        """Get all BSC indicators for a specific perspective in a period.
        
        Args:
            perspective: BSC perspective
            period_id: Period ID
            
        Returns:
            List of BSCIndicator objects
        """
        return await self.repository.get_by_perspective(perspective=perspective, period_id=period_id)
    
    async def search_indicators(
        self,
        *,
        perspective: Optional[BSCPerspective] = None,
        period_id: Optional[UUID] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Search BSC indicators with pagination.
        
        Args:
            perspective: Optional perspective filter
            period_id: Optional period filter
            code: Optional code filter (partial match)
            is_active: Optional active status filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with results and pagination info
        """
        skip = (page - 1) * page_size
        
        # Get data with pagination
        indicators = await self.repository.search(
            perspective=perspective,
            period_id=period_id,
            code=code,
            is_active=is_active,
            skip=skip,
            limit=page_size
        )
        
        # Get total count for pagination
        total = await self.repository.search_count(
            perspective=perspective,
            period_id=period_id,
            code=code,
            is_active=is_active
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "data": indicators,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    async def get_bsc_dashboard(self, period_id: UUID) -> Dict[str, Any]:
        """Get BSC dashboard data for a period.
        
        Args:
            period_id: Period ID
            
        Returns:
            Dashboard data with perspectives and totals
        """
        return await self.repository.get_dashboard_data(period_id=period_id)
    
    async def bulk_import_indicators(self, bulk_import: BSCBulkImport, created_by: Optional[UUID] = None) -> List[BSCIndicator]:
        """Bulk import BSC indicators.
        
        Args:
            bulk_import: Bulk import data
            created_by: UUID of the user creating the indicators
            
        Returns:
            List of created BSCIndicator objects
        """
        created_indicators = []
        
        for indicator_data in bulk_import.indicators:
            try:
                # Check if indicator already exists
                existing_indicator = await self.repository.get_by_code(
                    code=indicator_data.code, 
                    period_id=indicator_data.period_id
                )
                
                if existing_indicator:
                    # Skip existing indicators
                    continue
                
                # Create new indicator
                indicator = await self.repository.create(
                    obj_in=indicator_data.dict(), 
                    created_by=created_by
                )
                created_indicators.append(indicator)
                
            except Exception as e:
                # Log the error but continue with the next item
                print(f"Error importing indicator {indicator_data.code}: {str(e)}")
                continue
        
        return created_indicators


class BSCActualService(BaseService[BSCActual, BSCActualRepository]):
    """Service for BSC Actual management."""
    
    def __init__(self, session: Session = Depends(get_db)):
        """Initialize with database session."""
        super().__init__(repository=BSCActualRepository, session=session)
    
    async def create_actual(self, actual_in: BSCActualCreate, created_by: Optional[UUID] = None) -> BSCActual:
        """Create a new BSC actual.
        
        Args:
            actual_in: BSC actual creation data
            created_by: UUID of the user creating the actual
            
        Returns:
            Created BSCActual object
        """
        # Calculate score, active_weight, and other derived values
        # In a real implementation, these calculations would be more complex
        # and based on the indicator's weight, category, etc.
        indicator_repo = BSCIndicatorRepository(self.repository.session)
        indicator = await indicator_repo.get_or_404(id=actual_in.indicator_id)
        
        # Simple calculation for demo purposes
        # In production, this would be more sophisticated based on category and other factors
        achievement = actual_in.achievement / Decimal(100)
        score = indicator.weight * achievement
        active_weight = indicator.weight * Decimal(2)  # Example calculation
        total_score = score * Decimal(0.2)  # Example calculation
        
        # Create actual data with calculated fields
        actual_data = actual_in.dict()
        actual_data.update({
            "score": score,
            "active_weight": active_weight,
            "total_score": total_score,
            "score_akhir": total_score  # For simplicity, using the same value
        })
        
        return await self.repository.create(obj_in=actual_data, created_by=created_by)
    
    async def update_actual(
        self, 
        actual_id: UUID, 
        actual_in: BSCActualUpdate, 
        updated_by: Optional[UUID] = None
    ) -> BSCActual:
        """Update a BSC actual.
        
        Args:
            actual_id: UUID of the actual to update
            actual_in: BSC actual update data
            updated_by: UUID of the user updating the actual
            
        Returns:
            Updated BSCActual object
        """
        # Get existing actual
        db_actual = await self.repository.get_or_404(id=actual_id)
        
        # Update data
        update_data = actual_in.dict(exclude_unset=True)
        
        # Recalculate derived values if actual_value or achievement changed
        if "actual_value" in update_data or "achievement" in update_data:
            indicator_repo = BSCIndicatorRepository(self.repository.session)
            indicator = await indicator_repo.get_or_404(id=db_actual.indicator_id)
            
            # Get current achievement or use the one from update
            achievement = update_data.get("achievement", db_actual.achievement) / Decimal(100)
            
            # Recalculate
            score = indicator.weight * achievement
            active_weight = indicator.weight * Decimal(2)  # Example calculation
            total_score = score * Decimal(0.2)  # Example calculation
            
            # Update calculated fields
            update_data.update({
                "score": score,
                "active_weight": active_weight,
                "total_score": total_score,
                "score_akhir": total_score  # For simplicity, using the same value
            })
        
        # Update the actual
        return await self.repository.update(
            db_obj=db_actual, 
            obj_in=update_data, 
            updated_by=updated_by
        )
    
    async def get_actuals_by_indicator(self, indicator_id: UUID) -> List[BSCActual]:
        """Get all actuals for a BSC indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of BSCActual objects
        """
        return await self.repository.get_by_indicator(indicator_id=indicator_id)
    
    async def get_latest_actual(self, indicator_id: UUID) -> Optional[BSCActual]:
        """Get the latest actual for a BSC indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            Most recent BSCActual object, or None if no actuals
        """
        return await self.repository.get_latest_by_indicator(indicator_id=indicator_id)