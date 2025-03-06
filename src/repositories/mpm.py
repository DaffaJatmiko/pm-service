"""MPM (Management Performance Measurement) repository implementation for Performance Management System."""

from typing import Dict, List, Optional, Any, Tuple
from sqlmodel import Session, select, col, or_, func, and_
from uuid import UUID
from fastapi import HTTPException, status
from datetime import datetime, date
from decimal import Decimal

from src.models.mpm import (
    MPMIndicator, MPMMonthlyTarget, MPMActionPlan, 
    MPMQuarterlyData, MPMActual, MPMApprover,
    MPMPerspective, MPMUOM, MPMCategory, MPMCalculation, MPMStatus
)
from src.repositories.base import BaseRepository


class MPMIndicatorRepository(BaseRepository[MPMIndicator]):
    """Repository for MPM Indicator model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=MPMIndicator, session=session)
    
    async def get_by_kpi(self, kpi: str, period_id: UUID) -> Optional[MPMIndicator]:
        """Get a MPM indicator by KPI name and period.
        
        Args:
            kpi: KPI name
            period_id: Period ID
            
        Returns:
            MPMIndicator object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.kpi) == kpi,
            col(self.model.period_id) == period_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def get_by_period(self, period_id: UUID) -> List[MPMIndicator]:
        """Get all MPM indicators for a period.
        
        Args:
            period_id: Period ID
            
        Returns:
            List of MPMIndicator objects for the period
        """
        statement = select(self.model).where(
            col(self.model.period_id) == period_id,
            col(self.model.is_deleted) == False
        ).order_by(col(self.model.perspective), col(self.model.kpi_number))
        results = self.session.exec(statement)
        return results.all()
    
    async def get_by_perspective(self, perspective: MPMPerspective, period_id: UUID) -> List[MPMIndicator]:
        """Get all MPM indicators for a specific perspective in a period.
        
        Args:
            perspective: MPM perspective
            period_id: Period ID
            
        Returns:
            List of MPMIndicator objects for the perspective and period
        """
        statement = select(self.model).where(
            col(self.model.perspective) == perspective,
            col(self.model.period_id) == period_id,
            col(self.model.is_deleted) == False
        ).order_by(col(self.model.kpi_number))
        results = self.session.exec(statement)
        return results.all()
    
    async def get_by_id_with_related(self, id: UUID) -> Dict[str, Any]:
        """Get a MPM indicator with its related data.
        
        Args:
            id: Indicator ID
            
        Returns:
            Dictionary with indicator and related data
        """
        # Get the indicator
        indicator = await self.get_or_404(id=id)
        
        # Get monthly targets
        statement_targets = select(MPMMonthlyTarget).where(
            col(MPMMonthlyTarget.indicator_id) == id,
            col(MPMMonthlyTarget.is_deleted) == False
        ).order_by(col(MPMMonthlyTarget.month))
        results_targets = self.session.exec(statement_targets)
        monthly_targets = results_targets.all()
        
        # Get action plans
        statement_plans = select(MPMActionPlan).where(
            col(MPMActionPlan.indicator_id) == id,
            col(MPMActionPlan.is_deleted) == False
        )
        results_plans = self.session.exec(statement_plans)
        action_plans = results_plans.all()
        
        # Get actuals
        statement_actuals = select(MPMActual).where(
            col(MPMActual.indicator_id) == id,
            col(MPMActual.is_deleted) == False
        ).order_by(col(MPMActual.created_at).desc())
        results_actuals = self.session.exec(statement_actuals)
        actuals = results_actuals.all()
        
        # For each action plan, get quarterly data
        action_plans_with_quarters = []
        for action_plan in action_plans:
            statement_quarters = select(MPMQuarterlyData).where(
                col(MPMQuarterlyData.action_plan_id) == action_plan.id,
                col(MPMQuarterlyData.is_deleted) == False
            ).order_by(col(MPMQuarterlyData.quarter))
            results_quarters = self.session.exec(statement_quarters)
            quarterly_data = results_quarters.all()
            
            action_plan_data = action_plan.dict()
            action_plan_data["quarterly_data"] = quarterly_data
            action_plans_with_quarters.append(action_plan_data)
        
        return {
            "indicator": indicator,
            "monthly_targets": monthly_targets,
            "action_plans": action_plans_with_quarters,
            "actuals": actuals
        }
    
    async def search(
        self,
        *,
        perspective: Optional[MPMPerspective] = None,
        period_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MPMIndicator]:
        """Search MPM indicators with various filters.
        
        Args:
            perspective: Optional perspective filter
            period_id: Optional period filter
            is_active: Optional active status filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of MPMIndicator objects matching the criteria
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if perspective:
            statement = statement.where(col(self.model.perspective) == perspective)
        
        if period_id:
            statement = statement.where(col(self.model.period_id) == period_id)
        
        if is_active is not None:
            statement = statement.where(col(self.model.is_active) == is_active)
        
        # Order by perspective and KPI number
        statement = statement.order_by(col(self.model.perspective), col(self.model.kpi_number))
        
        statement = statement.offset(skip).limit(limit)
        results = self.session.exec(statement)
        return results.all()
    
    async def search_count(
        self,
        *,
        perspective: Optional[MPMPerspective] = None,
        period_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Count MPM indicators matching search criteria.
        
        Args:
            perspective: Optional perspective filter
            period_id: Optional period filter
            is_active: Optional active status filter
            
        Returns:
            Number of matching MPM indicators
        """
        statement = select(self.model).where(col(self.model.is_deleted) == False)
        
        # Apply filters
        if perspective:
            statement = statement.where(col(self.model.perspective) == perspective)
        
        if period_id:
            statement = statement.where(col(self.model.period_id) == period_id)
        
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
            "total_score": Decimal(0)
        }
        
        # Get period information
        # In a real implementation, this would come from the period repository
        # But for simplicity, we're using dummy data
        period_info = {
            "id": period_id,
            "name": "Jan-25",  # Placeholder
        }
        
        for indicator in indicators:
            # Extract the perspective name
            perspective = indicator.perspective or "Other"
            
            # Create perspective group if it doesn't exist
            if perspective not in data:
                data[perspective] = {
                    "items": [],
                    "total_weight": Decimal(0),
                    "total_score": Decimal(0)
                }
            
            # Get monthly targets
            statement_targets = select(MPMMonthlyTarget).where(
                col(MPMMonthlyTarget.indicator_id) == indicator.id,
                col(MPMMonthlyTarget.is_deleted) == False
            )
            results_targets = self.session.exec(statement_targets)
            monthly_targets = results_targets.all()
            
            # Convert to dictionary for easier access
            monthly_targets_dict = {target.month: target.target_value for target in monthly_targets}
            
            # Get the latest actual
            statement_actual = select(MPMActual).where(
                col(MPMActual.indicator_id) == indicator.id,
                col(MPMActual.is_deleted) == False
            ).order_by(col(MPMActual.created_at).desc())
            results_actual = self.session.exec(statement_actual)
            actual = results_actual.first()
            
            # Get action plans
            statement_plans = select(MPMActionPlan).where(
                col(MPMActionPlan.indicator_id) == indicator.id,
                col(MPMActionPlan.is_deleted) == False
            )
            results_plans = self.session.exec(statement_plans)
            action_plans = results_plans.all()
            
            # Add indicator data
            item = {
                "indicator": indicator,
                "monthly_targets": monthly_targets_dict,
                "actual": actual,
                "action_plans": action_plans
            }
            
            data[perspective]["items"].append(item)
            
            # Update perspective totals
            data[perspective]["total_weight"] += indicator.weight
            
            # Update overall totals
            totals["total_weight"] += indicator.weight
            
            if actual:
                data[perspective]["total_score"] += actual.score
                totals["total_score"] += actual.score
        
        # Convert to expected format
        result = {
            "period_id": period_id,
            "period_name": period_info["name"],
            "perspectives": [],
            **totals
        }
        
        for perspective, perspective_data in data.items():
            result["perspectives"].append({
                "perspective": perspective,
                **perspective_data
            })
        
        return result
    
    async def get_next_kpi_number(self, perspective: MPMPerspective, period_id: UUID) -> int:
        """Get the next KPI number for a perspective.
        
        Args:
            perspective: MPM perspective
            period_id: Period ID
            
        Returns:
            Next KPI number
        """
        statement = select(func.max(self.model.kpi_number)).where(
            col(self.model.perspective) == perspective,
            col(self.model.period_id) == period_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        max_number = results.one_or_none() or 0
        return max_number + 1


class MPMMonthlyTargetRepository(BaseRepository[MPMMonthlyTarget]):
    """Repository for MPM Monthly Target model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=MPMMonthlyTarget, session=session)
    
    async def get_by_indicator(self, indicator_id: UUID) -> List[MPMMonthlyTarget]:
        """Get all monthly targets for an indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of MPMMonthlyTarget objects for the indicator
        """
        statement = select(self.model).where(
            col(self.model.indicator_id) == indicator_id,
            col(self.model.is_deleted) == False
        ).order_by(col(self.model.month))
        results = self.session.exec(statement)
        return results.all()
    
    async def get_by_month(self, indicator_id: UUID, month: str) -> Optional[MPMMonthlyTarget]:
        """Get a monthly target by indicator and month.
        
        Args:
            indicator_id: Indicator ID
            month: Month string (e.g., "Jan-25")
            
        Returns:
            MPMMonthlyTarget object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.indicator_id) == indicator_id,
            col(self.model.month) == month,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()


class MPMActionPlanRepository(BaseRepository[MPMActionPlan]):
    """Repository for MPM Action Plan model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=MPMActionPlan, session=session)
    
    async def get_by_indicator(self, indicator_id: UUID) -> List[MPMActionPlan]:
        """Get all action plans for an indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of MPMActionPlan objects for the indicator
        """
        statement = select(self.model).where(
            col(self.model.indicator_id) == indicator_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()
    
    async def get_by_id_with_quarters(self, action_plan_id: UUID) -> Dict[str, Any]:
        """Get an action plan with its quarterly data.
        
        Args:
            action_plan_id: Action Plan ID
            
        Returns:
            Dictionary with action plan and quarterly data
        """
        # Get the action plan
        action_plan = await self.get_or_404(id=action_plan_id)
        
        # Get quarterly data
        statement = select(MPMQuarterlyData).where(
            col(MPMQuarterlyData.action_plan_id) == action_plan_id,
            col(MPMQuarterlyData.is_deleted) == False
        ).order_by(col(MPMQuarterlyData.quarter))
        results = self.session.exec(statement)
        quarterly_data = results.all()
        
        return {
            "action_plan": action_plan,
            "quarterly_data": quarterly_data
        }
    
    async def calculate_status(self, action_plan_id: UUID) -> MPMStatus:
        """Calculate status for an action plan based on quarterly data.
        
        Args:
            action_plan_id: Action Plan ID
            
        Returns:
            Calculated status
        """
        # Get the most recent quarter with actual data
        statement = select(MPMQuarterlyData).where(
            col(MPMQuarterlyData.action_plan_id) == action_plan_id,
            col(MPMQuarterlyData.actual_value) != None,
            col(MPMQuarterlyData.is_deleted) == False
        ).order_by(col(MPMQuarterlyData.quarter).desc())
        results = self.session.exec(statement)
        latest_quarter = results.first()
        
        if not latest_quarter:
            return MPMStatus.ON_TRACK  # Default if no actual data
        
        # Calculate status based on the actual vs target ratio
        if latest_quarter.actual_value >= latest_quarter.target_value:
            return MPMStatus.ON_TRACK
        elif latest_quarter.actual_value >= latest_quarter.target_value * Decimal('0.8'):
            return MPMStatus.AT_RISK
        else:
            return MPMStatus.OFF_TRACK
    
    async def get_quarterly_summary(self) -> List[Dict[str, Any]]:
        """Get quarterly summary of action plans.
        
        Returns:
            List of quarterly summary data
        """
        # This is a placeholder implementation - in a real application, 
        # you would calculate this based on actual data in the database
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        current_year = datetime.now().year
        
        summary = []
        for i, quarter in enumerate(quarters):
            # Determine if quarter is current or past
            is_past = i <= 1  # Assuming Q1 and Q2 are in the past for this example
            
            # Create summary for each quarter
            summary.append({
                "quarter": f"{quarter} {current_year}",
                "completion": "100%" if is_past else "0%",
                "on_track_count": 1 if is_past else 0,
                "at_risk_count": 1 if is_past else 0,
                "off_track_count": 0
            })
        
        return summary


class MPMQuarterlyDataRepository(BaseRepository[MPMQuarterlyData]):
    """Repository for MPM Quarterly Data model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=MPMQuarterlyData, session=session)
    
    async def get_by_action_plan(self, action_plan_id: UUID) -> List[MPMQuarterlyData]:
        """Get all quarterly data for an action plan.
        
        Args:
            action_plan_id: Action Plan ID
            
        Returns:
            List of MPMQuarterlyData objects for the action plan
        """
        statement = select(self.model).where(
            col(self.model.action_plan_id) == action_plan_id,
            col(self.model.is_deleted) == False
        ).order_by(col(self.model.quarter))
        results = self.session.exec(statement)
        return results.all()
    
    async def get_by_quarter(self, action_plan_id: UUID, quarter: str) -> Optional[MPMQuarterlyData]:
        """Get quarterly data by action plan and quarter.
        
        Args:
            action_plan_id: Action Plan ID
            quarter: Quarter string (e.g., "Q1")
            
        Returns:
            MPMQuarterlyData object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.action_plan_id) == action_plan_id,
            col(self.model.quarter) == quarter,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()


class MPMActualRepository(BaseRepository[MPMActual]):
    """Repository for MPM Actual model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=MPMActual, session=session)
    
    async def get_by_indicator(self, indicator_id: UUID) -> List[MPMActual]:
        """Get all actuals for an indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            List of MPMActual objects for the indicator
        """
        statement = select(self.model).where(
            col(self.model.indicator_id) == indicator_id,
            col(self.model.is_deleted) == False
        ).order_by(col(self.model.created_at).desc())
        results = self.session.exec(statement)
        return results.all()
    
    async def get_latest_by_indicator(self, indicator_id: UUID) -> Optional[MPMActual]:
        """Get the latest actual for an indicator.
        
        Args:
            indicator_id: Indicator ID
            
        Returns:
            Most recent MPMActual object for the indicator, or None if no actuals
        """
        statement = select(self.model).where(
            col(self.model.indicator_id) == indicator_id,
            col(self.model.is_deleted) == False
        ).order_by(col(self.model.created_at).desc())
        results = self.session.exec(statement)
        return results.first()


class MPMApproverRepository(BaseRepository[MPMApprover]):
    """Repository for MPM Approver model."""
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        super().__init__(model=MPMApprover, session=session)
    
    async def get_by_user(self, user_id: UUID) -> Optional[MPMApprover]:
        """Get an approver by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            MPMApprover object if found, None otherwise
        """
        statement = select(self.model).where(
            col(self.model.user_id) == user_id,
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.first()
    
    async def get_all_approvers(self) -> List[MPMApprover]:
        """Get all MPM approvers.
        
        Returns:
            List of all MPMApprover objects
        """
        statement = select(self.model).where(
            col(self.model.is_deleted) == False
        )
        results = self.session.exec(statement)
        return results.all()