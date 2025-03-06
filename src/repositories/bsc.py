"""BSC (Balanced Scorecard) repository implementation for Performance Management System."""

from typing import Dict, List, Optional, Any, Union
from sqlmodel import Session, select, col, or_, func, and_
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime
from decimal import Decimal

from src.models.bsc import BSCIndicator, BSCActual, BSCPerspective, BSCUOM, BSCCategory, BSCCalculation
from src.repositories.base import BaseRepository


class BSCIndicatorRepository(BaseRepository[BSCIndicator]):
    """Repository for BSC Indicator model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=BSCIndicator, session=session)
    
    async def get_by_code(self, code: str, period_id: UUID) -> Optional[BSCIndicator]:
        """Get a BSC indicator by code and period.
        
        Args:
            code: Indicator code
            period_id: Period ID
            
        Returns:
            BSCIndicator object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.code) == code,
            col(self.model.period_id) == period_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def get_by_period(self, period_id: UUID) -> List[BSCIndicator]:
        """Get all BSC indicators for a period.
        
        Args:
            period_id: Period ID
            
        Returns:
            List of BSCIndicator objects for the period
        """
        statement = select(self.model).where(
            col(self.model.period_id) == period_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()
    
    async def get_by_perspective(self, perspective: BSCPerspective, period_id: UUID) -> List[BSCIndicator]:
        """Get all BSC indicators for a specific perspective in a period.
        
        Args:
            perspective: BSC perspective
            period_id: Period ID
            
        Returns:
            List of BSCIndicator objects for the perspective and period
        """
        statement = select(self.model).where(
            col(self.model.perspective) == perspective,
            col(self.model.period_id) == period_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()
    
    async def get_by_id_with_actuals(self, id: UUID) -> Dict[str, Any]:
        """Get a BSC indicator with its actuals.
        
        Args:
            id: Indicator ID
            
        Returns:
            Dictionary with indicator and actuals
        """
        # Get the indicator
        indicator = await self.get_or_404(id=id)
        
        # Get the actuals for this indicator
        statement = select(BSCActual).where(
            col(BSCActual.indicator_id) == id,
            col(BSCActual.is_deleted) == False
        )
        results = self.session.exec(statement)
        actuals = results.all()
        
        return {
            "indicator": indicator,
            "actuals": actuals
        }
    
    async def search(
        self,
        *,
        perspective: Optional[BSCPerspective] = None,
        period_id: Optional[UUID] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BSCIndicator]:
        """Search BSC indicators with various filters.
        
        Args:
            perspective: Optional perspective filter
            period_id: Optional period filter
            code: Optional code filter (partial match)
            is_active: Optional active status filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of BSCIndicator objects matching the criteria
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if perspective:
            statement = statement.where(col(self.model.perspective) == perspective)
        
        if period_id:
            statement = statement.where(col(self.model.period_id) == period_id)
        
        if code:
            statement = statement.where(col(self.model.code).contains(code))
        
        if is_active is not None:
            statement = statement.where(col(self.model.is_active) == is_active)
        
        statement = statement.offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    async def search_count(
        self,
        *,
        perspective: Optional[BSCPerspective] = None,
        period_id: Optional[UUID] = None,
        code: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Count BSC indicators matching search criteria.
        
        Args:
            perspective: Optional perspective filter
            period_id: Optional period filter
            code: Optional code filter (partial match)
            is_active: Optional active status filter
            
        Returns:
            Number of matching BSC indicators
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if perspective:
            statement = statement.where(col(self.model.perspective) == perspective)
        
        if period_id:
            statement = statement.where(col(self.model.period_id) == period_id)
        
        if code:
            statement = statement.where(col(self.model.code).contains(code))
        
        if is_active is not None:
            statement = statement.where(col(self.model.is_active) == is_active)
        
        results = self.session.exec(statement)
        return len(results.all())
    
    async def get_dashboard_data(self, period_id: UUID) -> Dict[str, Any]:
        """Get dashboard data for a specific period, grouped by perspective.
        
        Args:
            period_id: Period ID
            
        Returns:
            Dictionary with dashboard data
        """
        # Get all indicators for the period
        indicators = await self.get_by_period(period_id=period_id)
        
        # Group by perspective
        data = {}
        totals = {
            "total_weight": Decimal(0),
            "total_score": Decimal(0),
            "total_active_weight": Decimal(0),
            "total_score_akhir": Decimal(0)
        }
        
        # Get period information
        # In a real implementation, this would come from the period repository
        # But for simplicity, we're using dummy data
        period_info = {
            "id": period_id,
            "name": "Jan-25",  # Placeholder
            "type": "Monthly"  # Placeholder
        }
        
        for indicator in indicators:
            # Get actuals for this indicator
            statement = select(BSCActual).where(
                col(BSCActual.indicator_id) == indicator.id,
                col(BSCActual.is_deleted) == False
            )
            results = self.session.exec(statement)
            actuals = results.all()
            
            # Extract the perspective name
            perspective = indicator.perspective
            
            # Create perspective group if it doesn't exist
            if perspective not in data:
                data[perspective] = {
                    "items": [],
                    "total_weight": Decimal(0),
                    "total_score": Decimal(0),
                    "total_active_weight": Decimal(0),
                    "total_score_akhir": Decimal(0)
                }
            
            # Add indicator data with most recent actual (if any)
            item = {
                "indicator": indicator,
                "actual": actuals[0] if actuals else None
            }
            
            data[perspective]["items"].append(item)
            
            # Update perspective totals
            data[perspective]["total_weight"] += indicator.weight
            
            # Update overall totals
            totals["total_weight"] += indicator.weight
            
            if actuals:
                actual = actuals[0]
                data[perspective]["total_score"] += actual.score
                data[perspective]["total_active_weight"] += actual.active_weight
                data[perspective]["total_score_akhir"] += actual.score_akhir
                
                totals["total_score"] += actual.score
                totals["total_active_weight"] += actual.active_weight
                totals["total_score_akhir"] += actual.score_akhir
        
        # Convert to expected format
        result = {
            "period_id": period_id,
            "period_name": period_info["name"],
            "bsc_type": period_info["type"],
            "perspectives": [],
            **totals
        }
        
        for perspective, perspective_data in data.items():
            result["perspectives"].append({
                "perspective": perspective,
                **perspective_data
            })
        
        return result


class BSCActualRepository(BaseRepository[BSCActual]):
    """Repository for BSC Actual model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=BSCActual, session=session)
    
    async def get_by_indicator(self, indicator_id: UUID) -> List[BSCActual]:
        """Get all actuals for a BSC indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of BSCActual objects for the indicator
        """
        statement = select(self.model).where(
            col(self.model.indicator_id) == indicator_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()
    
    async def get_latest_by_indicator(self, indicator_id: UUID) -> Optional[BSCActual]:
        """Get the latest actual for a BSC indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            Most recent BSCActual object for the indicator, or None if no actuals
        """
        statement = select(self.model).where(
            col(self.model.indicator_id) == indicator_id,
            col(self.model.is_deleted) == False
        ).order_by(col(self.model.created_at).desc())
        results = self.session.exec(statement)
        return results.first()